from __future__ import annotations

import copy
import random
from typing import Dict, Iterator, List, Optional, Tuple

from framework.dimensions.classification_distribution import VerifierSlot
from framework.grids import GridPair, is_equal_grid
from framework.tasks.arc_dataset import list_arc_agi_1_task_ids, load_task
from framework.tasks.base import ArcTask, Verifier
from framework.verifier_selection import (
    clear_verifier_csv_cache,
    csv_slots_for_task,
    default_verifiers_csv_path,
    eligible_task_ids_from_csv,
    list_valid_verifiers_from_csv,
)

_VALID_VERIFIERS_CACHE: Dict[str, List[Tuple[VerifierSlot, Verifier]]] = {}

# Slots preferred, in order, whenever one is among a task's valid verifiers.
# ``custom`` comes first: those are hand-written verifiers in
# ``framework/custom_verifiers``, several of which exist precisely to fix a bug in
# the slot they replace. ``re_arc`` comes next; the golf slots
# (google/keymoon/neurips) often hardcode ARC-GEN grid shapes and answer
# off-distribution queries with garbage instead of raising, so they are last.
PREFERRED_SLOTS: tuple[VerifierSlot, ...] = ("custom", "re_arc")
PREFERRED_SLOT: VerifierSlot = PREFERRED_SLOTS[0]  # back-compat

# task_id -> index into ``list_valid_verifiers(task)``, fixed on first pick so a
# task keeps one verifier for every operation in this process (queries, hot
# start, test sampling, answer checking) and across trials in the same session.
_SESSION_VERIFIER_PIN: Dict[str, int] = {}


def clear_verifier_caches() -> None:
    """Drop cached verifier lists, session pins and CSV cache (for tests)."""
    _VALID_VERIFIERS_CACHE.clear()
    _SESSION_VERIFIER_PIN.clear()
    clear_verifier_csv_cache()


def list_valid_verifiers(task: ArcTask) -> List[Tuple[VerifierSlot, Verifier]]:
    """Return valid verifiers for *task* (CSV fast path; no dynamic50 re-probe at runtime)."""
    cached = _VALID_VERIFIERS_CACHE.get(task.task_id)
    if cached is not None:
        return cached

    if task.arc_gen_generator is None:
        _VALID_VERIFIERS_CACHE[task.task_id] = []
        return []

    fast = list_valid_verifiers_from_csv(task)
    out: List[Tuple[VerifierSlot, Verifier]] = list(fast) if fast is not None else []

    # A verifier written in framework/custom_verifiers takes precedence over the
    # vendored ARC-AGI-2 candidates, which share the same ``custom`` slot: the
    # local ones exist precisely because a vendored verifier was wrong or crashed.
    if fast is None and task.quinary_verifier is not None:
        try:
            from framework.custom_verifiers.registry import has_local_verifier

            if has_local_verifier(task.task_id):
                out.insert(0, ("custom", task.quinary_verifier))
        except Exception:
            pass

    # Pre-validated ARC-AGI-2 standalone verifiers (official + 250 ARC-GEN).
    # Already offline-audited; do not re-probe dynamic50 here.
    added_agi2 = False
    try:
        from framework.integrations.agi2_verifiers import get_agi2_valid_verifiers

        seen = {id(fn) for _, fn in out}
        for _cid, fn in get_agi2_valid_verifiers(task.task_id):
            if id(fn) in seen:
                continue
            out.append(("custom", fn))
            seen.add(id(fn))
            added_agi2 = True
    except Exception:
        pass

    if fast is None and not added_agi2 and not out:
        from framework.verifier_selection import _legacy_valid_verifiers

        out = _legacy_valid_verifiers(task)

    _VALID_VERIFIERS_CACHE[task.task_id] = out
    return out


def pinned_verifier(task: ArcTask) -> Optional[Tuple[VerifierSlot, Verifier]]:
    """Verifier already pinned for *task* in this session, or ``None``."""
    idx = _SESSION_VERIFIER_PIN.get(task.task_id)
    if idx is None:
        return None
    valid = list_valid_verifiers(task)
    if idx >= len(valid):
        return None
    return valid[idx]


def pin_verifier(task_id: str, index: int) -> None:
    """Fix the verifier a task uses for the rest of this session."""
    _SESSION_VERIFIER_PIN[task_id] = int(index)


def clear_verifier_pins() -> None:
    """Forget session verifier pins (keeps the valid-verifier cache)."""
    _SESSION_VERIFIER_PIN.clear()


def pick_verifier(
    task: ArcTask, rng: random.Random
) -> Optional[Tuple[VerifierSlot, Verifier]]:
    """Choose one verifier for *task* and pin it for the rest of the session.

    Order: a pin from an earlier trial in this session, then ``custom``, then
    ``re_arc``, then a uniform sample among the remaining slots.
    Returns ``None`` if the task has no valid verifier.
    """
    valid = list_valid_verifiers(task)
    if not valid:
        return None

    pinned = pinned_verifier(task)
    if pinned is not None:
        return pinned

    index = None
    for preferred in PREFERRED_SLOTS:
        index = next((i for i, (slot, _) in enumerate(valid) if slot == preferred), None)
        if index is not None:
            break
    if index is None:
        index = rng.randrange(len(valid))
    pin_verifier(task.task_id, index)
    return valid[index]


# Back-compat alias: selection is no longer uniform when ``re_arc`` is available.
pick_random_verifier = pick_verifier


def _list_original_task_ids() -> List[str]:
    return list_arc_agi_1_task_ids()


def iter_eligible_tasks(rng: random.Random) -> Iterator[Tuple[str, ArcTask]]:
    """Yield tasks with ARC-GEN dynamic generation and ≥1 valid verifier."""
    use_csv = default_verifiers_csv_path().is_file()
    ids = eligible_task_ids_from_csv() if use_csv else _list_original_task_ids()
    if not ids:
        return
    order = ids[:]
    rng.shuffle(order)
    for task_id in order:
        try:
            task = load_task(task_id, load_alternative_verifiers=False)
        except Exception:
            continue
        if task.arc_gen_generator is None:
            continue
        if use_csv:
            if csv_slots_for_task(task_id):
                yield task_id, task
            continue
        if list_valid_verifiers(task):
            yield task_id, task


def pick_random_eligible_task_id(rng: random.Random) -> Tuple[str, ArcTask]:
    """Pick a task that has ARC-GEN dynamic generation and ≥1 fully-valid verifier."""
    for item in iter_eligible_tasks(rng):
        return item
    raise RuntimeError(
        "No eligible task found (need ARC-GEN dynamic + ≥1 verifier). "
        "Check external data and task_valid_verifiers.csv."
    )


def _generate_dynamic_pairs(
    task: ArcTask,
    num_examples: int,
    rng: random.Random,
) -> List[GridPair]:
    gen = task.arc_gen_generator
    if gen is None:
        raise ValueError("Task has no dynamic generator")
    try:
        return gen(num_examples, rng)
    except TypeError:
        return gen(num_examples)


def sample_consistent_dynamic_pair(
    task: ArcTask,
    verifier: Verifier,
    rng: random.Random,
    *,
    exclude_inputs: Optional[List] = None,
    max_tries: int = 48,
) -> Optional[GridPair]:
    """Sample one dynamic generator pair consistent with the trial *verifier*.

    ARC-GEN (and similar) generators attach a labeled output to each input. In the
    common case that label matches every validated verifier, the first draw would
    suffice. We still re-roll because:

    - the trial uses one chosen verifier slot, which can disagree with the label on
      rare or ambiguous generator samples;
    - generator or verifier calls can throw on malformed edge cases.

    This is a safety filter, not because labels are usually wrong.
    """
    if task.arc_gen_generator is None:
        return None
    excluded = exclude_inputs or []
    for _ in range(max_tries):
        try:
            pair = copy.deepcopy(_generate_dynamic_pairs(task, 1, rng)[0])
        except Exception:
            continue
        if any(is_equal_grid(pair.input, ex) for ex in excluded):
            continue
        try:
            out = verifier(copy.deepcopy(pair.input))
        except Exception:
            continue
        if is_equal_grid(out, pair.output):
            return pair
    return None
