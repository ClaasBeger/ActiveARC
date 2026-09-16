"""Slippage trials: narrow hot-start, broad discovery and test.

Identical to a normal ActiveARC discovery trial except where the grids come from:

* **hot start** — one ARC-GEN pair consistent with the task's *narrow* verifier
  (the previously-valid hypothesis the model is seeded with);
* **queries and test** — the *broad* ``re_arc`` verifier, with test inputs drawn
  from the RE-ARC distribution, where the narrow hypothesis breaks down.

One narrow slot is used per task: the canonical (worst-slipping) slot recorded in
``experiments/slippage/slippage_pairs.json``, so each task runs exactly once.
"""

from __future__ import annotations

import copy
import json
import random
from dataclasses import dataclass, fields
from pathlib import Path

from framework.repo_paths import ACTIVEARC_ROOT as _REPO_ROOT
from typing import Dict, List, Optional

from framework.active_arc.headless_trial import ActiveArcTrialSession, create_trial_session
from framework.active_arc.verifier_selection import sample_consistent_dynamic_pair
from framework.grids import Grid, GridPair, is_equal_grid
from framework.tasks.arc_dataset import ensure_verifier_slots
from framework.tasks.base import ArcTask, Verifier
from framework.verifier_selection import VerifierSlot, _callable_for_slot

# Worktree-aware: bundled data lives in the main checkout.
_ROOT = _REPO_ROOT
DEFAULT_PAIRS_PATH = _ROOT / "experiments" / "slippage" / "slippage_pairs.json"

BROAD_SLOT: VerifierSlot = "re_arc"


def canonical_narrow_slots(pairs_path: Path | None = None) -> Dict[str, VerifierSlot]:
    """Map task id -> the one narrow slot to use (highest RE-ARC fail rate)."""
    path = pairs_path or DEFAULT_PAIRS_PATH
    if not path.is_file():
        raise FileNotFoundError(
            f"No slippage pairs at {path}. Build them with "
            "`python -m pipelines.find_slippage_pairs`."
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    meta = payload.get("meta") or {}
    canonical = meta.get("canonical_narrow_by_task")
    if isinstance(canonical, dict) and canonical:
        return {str(k): v for k, v in canonical.items()}
    # Older artifacts: recover the canonical slot from the pair rows.
    best: Dict[str, tuple] = {}
    for row in payload.get("pairs") or []:
        key = (row.get("narrow_fail_rate", 0.0), row.get("narrow_fail_count", 0))
        tid = row.get("task_id")
        if tid and (tid not in best or key > best[tid][0]):
            best[tid] = (key, row.get("narrow_slot"))
    return {tid: slot for tid, (_k, slot) in best.items()}


def slippage_task_ids(pairs_path: Path | None = None) -> List[str]:
    """Task ids with a slippage pair, one entry each."""
    return sorted(canonical_narrow_slots(pairs_path))


@dataclass
class SlippageTrialSession(ActiveArcTrialSession):
    """Discovery trial whose test pairs come from the broad (RE-ARC) distribution."""

    narrow_slot: Optional[VerifierSlot] = None
    hot_start_broad_agrees: Optional[bool] = None

    def _sample_test_pair(self) -> Optional[GridPair]:
        exclude: List[Grid] = []
        if self.hot_start_pair is not None:
            exclude.append(self.hot_start_pair.input)
        for _, test_in in self.shown_test_inputs:
            exclude.append(test_in)
        return sample_broad_pair(
            self.task,
            self._verifier_fn(),
            self.rng,
            exclude_inputs=exclude or None,
        )


def sample_broad_pair(
    task: ArcTask,
    verifier: Verifier,
    rng: random.Random,
    *,
    exclude_inputs: Optional[List[Grid]] = None,
    max_tries: int = 48,
) -> Optional[GridPair]:
    """Sample one RE-ARC pair consistent with the broad *verifier*.

    Prefers the live RE-ARC generator and falls back to the committed stable pool.
    """
    gen = task.re_arc_generator
    pool = list(task.re_arc_synthetic_pairs or [])
    excluded = exclude_inputs or []
    for _ in range(max_tries):
        pair: Optional[GridPair] = None
        if gen is not None:
            try:
                pair = copy.deepcopy(gen(1)[0])
            except Exception:
                pair = None
        if pair is None and pool:
            pair = copy.deepcopy(rng.choice(pool))
        if pair is None:
            return None
        if any(is_equal_grid(pair.input, ex) for ex in excluded):
            continue
        try:
            out = verifier(copy.deepcopy(pair.input))
        except Exception:
            continue
        if is_equal_grid(out, pair.output):
            return pair
    return None


def _narrow_verifier(task: ArcTask, slot: VerifierSlot) -> Verifier:
    ensure_verifier_slots(task, [slot])
    fn = _callable_for_slot(task, slot)
    if fn is None:
        raise ValueError(f"Narrow verifier {slot!r} not loadable for {task.task_id!r}")
    return fn


def create_slippage_trial_session(
    *,
    seed: int,
    task_id: str,
    hot_start: bool = True,
    noisy_science: bool = False,
    re_trials: bool = False,
    wrong_answer_penalty: int = 0,
    fixed_test: bool = False,
    noise_probability: float = 0.12,
    narrow_slot: Optional[VerifierSlot] = None,
    pairs_path: Path | None = None,
) -> SlippageTrialSession:
    """Build a slippage trial for *task_id* (narrow hot start, broad queries/test).

    ``narrow_slot`` defaults to the task's canonical slot from the pairs artifact.
    """
    if narrow_slot is None:
        slots = canonical_narrow_slots(pairs_path)
        if task_id not in slots:
            raise ValueError(f"No slippage pair recorded for task {task_id!r}")
        narrow_slot = slots[task_id]

    # Base trial supplies the task, RNG and the pinned broad verifier. Hot start
    # and test pair are replaced below, so neither is sampled here.
    base = create_trial_session(
        seed=seed,
        task_id=task_id,
        hot_start=False,
        noisy_science=noisy_science,
        re_trials=re_trials,
        wrong_answer_penalty=wrong_answer_penalty,
        fixed_test=False,
        noise_probability=noise_probability,
        dataset="arc",
    )
    if base.verifier_slot != BROAD_SLOT:
        raise ValueError(
            f"Task {task_id!r} did not select the broad {BROAD_SLOT!r} verifier "
            f"(got {base.verifier_slot!r}); it is not a usable slippage task."
        )

    session = SlippageTrialSession(
        **{f.name: getattr(base, f.name) for f in fields(ActiveArcTrialSession)},
        narrow_slot=narrow_slot,
    )
    session.hot_start = hot_start
    broad_fn = session._verifier_fn()

    if hot_start:
        narrow_fn = _narrow_verifier(session.task, narrow_slot)
        hot = sample_consistent_dynamic_pair(session.task, narrow_fn, session.rng)
        if hot is None:
            raise ValueError(
                f"Could not sample a narrow hot-start pair for {task_id!r}; try another seed."
            )
        session.hot_start_pair = hot
        try:
            session.hot_start_broad_agrees = is_equal_grid(
                broad_fn(copy.deepcopy(hot.input)), hot.output
            )
        except Exception:
            session.hot_start_broad_agrees = False

    session.fixed_test = fixed_test
    if fixed_test:
        test_pair = session._sample_test_pair()
        if test_pair is None:
            raise ValueError(
                f"Could not sample a broad test pair for {task_id!r}; try another seed."
            )
        session.test_pair = test_pair
    else:
        session.test_pair = None
    return session
