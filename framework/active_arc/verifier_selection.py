from __future__ import annotations

import copy
import random
from typing import Iterator, List, Optional, Tuple

from framework.dimensions.classification_distribution import (
    VerifierSlot,
    verifier_matches_train_test_stable_dynamic50,
)
from framework.grids import GridPair, is_equal_grid
from framework.tasks.arc_dataset import ARC_ORIGINAL_DIR, load_task
from framework.tasks.base import ArcTask, Verifier


def _candidate_slots(task: ArcTask) -> List[Tuple[VerifierSlot, Optional[Verifier]]]:
    return [
        ("re_arc", task.verifier),
        ("google", task.secondary_verifier),
        ("keymoon", task.tertiary_verifier),
        ("neurips", task.quaternary_verifier),
        ("custom", task.quinary_verifier),
    ]


def list_valid_verifiers(task: ArcTask) -> List[Tuple[VerifierSlot, Verifier]]:
    """All verifier implementations that pass train / test / stable / 50×dynamic checks."""
    out: List[Tuple[VerifierSlot, Verifier]] = []
    for name, fn in _candidate_slots(task):
        if fn is None:
            continue
        if verifier_matches_train_test_stable_dynamic50(task, fn):
            out.append((name, fn))
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
    """Yield tasks that have ARC-GEN dynamic generation and ≥1 fully-valid verifier."""
    ids = _list_original_task_ids()
    if not ids:
        return
    order = ids[:]
    rng.shuffle(order)
    for task_id in order:
        try:
            task = load_task(task_id)
        except Exception:
            continue
        if task.arc_gen_generator is None:
            continue
        if not list_valid_verifiers(task):
            continue
        yield task_id, task


def pick_random_eligible_task_id(rng: random.Random) -> Tuple[str, ArcTask]:
    """Pick a task that has ARC-GEN dynamic generation and ≥1 fully-valid verifier."""
    for item in iter_eligible_tasks(rng):
        return item
    raise RuntimeError(
        "No eligible task found (need ARC-GEN dynamic + ≥1 verifier passing "
        "train/test/stable/dynamic50). Check external data and verifier setup."
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
