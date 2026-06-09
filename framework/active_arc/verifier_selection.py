from __future__ import annotations

import copy
import random
from typing import Dict, Iterator, List, Optional, Tuple

from framework.dimensions.classification_distribution import VerifierSlot
from framework.grids import GridPair, is_equal_grid
from framework.tasks.arc_dataset import ARC_ORIGINAL_DIR, load_task
from framework.tasks.base import ArcTask, Verifier
from framework.verifier_selection import (
    clear_verifier_csv_cache,
    csv_slots_for_task,
    default_verifiers_csv_path,
    eligible_task_ids_from_csv,
    list_valid_verifiers_from_csv,
)

_VALID_VERIFIERS_CACHE: Dict[str, List[Tuple[VerifierSlot, Verifier]]] = {}


def clear_verifier_caches() -> None:
    """Drop cached verifier lists and CSV cache (for tests)."""
    _VALID_VERIFIERS_CACHE.clear()
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
    if fast is not None:
        _VALID_VERIFIERS_CACHE[task.task_id] = fast
        return fast

    from framework.verifier_selection import _legacy_valid_verifiers

    out = _legacy_valid_verifiers(task)
    _VALID_VERIFIERS_CACHE[task.task_id] = out
    return out


def pick_random_verifier(
    task: ArcTask, rng: random.Random
) -> Optional[Tuple[VerifierSlot, Verifier]]:
    """Uniformly sample among all valid verifiers, or ``None`` if none qualify."""
    valid = list_valid_verifiers(task)
    if not valid:
        return None
    return rng.choice(valid)


def _list_original_task_ids() -> List[str]:
    if not ARC_ORIGINAL_DIR.exists():
        return []
    ids = [p.stem for p in ARC_ORIGINAL_DIR.glob("*.json")]
    ids.sort()
    return ids


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


def sample_consistent_dynamic_pair(
    task: ArcTask,
    verifier: Verifier,
    rng: random.Random,
    *,
    max_tries: int = 48,
) -> Optional[GridPair]:
    """Sample one ARC-GEN dynamic pair where *verifier* matches the labeled output."""
    if task.arc_gen_generator is None:
        return None
    for _ in range(max_tries):
        try:
            pair = copy.deepcopy(task.arc_gen_generator(1)[0])
        except Exception:
            continue
        try:
            out = verifier(copy.deepcopy(pair.input))
        except Exception:
            continue
        if is_equal_grid(out, pair.output):
            return pair
    return None
