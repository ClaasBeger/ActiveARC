"""The sampled held-out item each task is scored on, frozen once and shared.

Every arm has to answer the *same* sampled item or the column comparing them
means nothing, and deriving it live does not give that: the pair comes off the
session RNG, so an arm that draws its own demonstration pairs first advances the
stream and lands on a different item. The random-K arm does exactly that.

So the item is drawn once, before anything else consumes the RNG, and written to
``experiments/eval_items/<dataset>_seed<seed>.json``. Thereafter every arm reads
it. That also pins the item against future changes to sampling, which a live
draw would silently follow.

The frozen values reproduce what the recorded active trials already used --
verified across all 400 ARC-AGI-1 tasks -- so freezing costs none of the runs
already on disk.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from framework.repo_paths import ACTIVEARC_ROOT

EVAL_ITEMS_DIR = ACTIVEARC_ROOT / "experiments" / "eval_items"

_CACHE: Dict[Tuple[str, int], Dict[str, Any]] = {}


def manifest_path(dataset: str, seed: int) -> Path:
    return EVAL_ITEMS_DIR / f"{dataset}_seed{seed}.json"


def load_manifest(dataset: str, seed: int) -> Dict[str, Any]:
    key = (dataset, seed)
    if key not in _CACHE:
        p = manifest_path(dataset, seed)
        if p.is_file():
            _CACHE[key] = json.loads(p.read_text(encoding="utf-8")).get("items", {})
        else:
            _CACHE[key] = {}
    return _CACHE[key]


def sampled_item(dataset: str, seed: int, task_id: str) -> Optional[Tuple[List, List]]:
    """The frozen (input, output) for this task, or None if it was never frozen."""
    entry = load_manifest(dataset, seed).get(task_id)
    if not entry:
        return None
    return entry["input"], entry["output"]


def draw_sampled_item(dataset: str, seed: int, task_id: str) -> Optional[Tuple[List, List]]:
    """Draw the item the way it must be drawn to be canonical: first, from a clean session.

    Used to build the manifest. Anything that consumes the session RNG before
    this -- drawing demonstration pairs, for instance -- changes the answer,
    which is the whole reason the result gets frozen.
    """
    from framework.active_arc.headless_trial import create_trial_session

    session = create_trial_session(seed=seed, task_id=task_id, dataset=dataset)
    pair = session._sample_test_pair()
    if pair is None:
        return None
    return pair.input, pair.output


def resolve_sampled_item(
    dataset: str, seed: int, task_id: str, *, allow_draw: bool = True
) -> Optional[Tuple[List, List]]:
    """Frozen item if there is one, otherwise draw it canonically."""
    got = sampled_item(dataset, seed, task_id)
    if got is not None:
        return got
    return draw_sampled_item(dataset, seed, task_id) if allow_draw else None
