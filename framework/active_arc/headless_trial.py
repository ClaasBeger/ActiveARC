"""Headless ActiveARC trial: same rules as ``interface/active_arc_app`` without Streamlit."""

from __future__ import annotations

import copy
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple

from framework.active_arc.query_noise import maybe_corrupt_query_output
from framework.active_arc.verifier_selection import (
    iter_eligible_tasks,
    list_valid_verifiers,
    sample_consistent_dynamic_pair,
)
from framework.dimensions.classification_distribution import VerifierSlot
from framework.grids import Grid, GridPair, clone_grid, is_equal_grid, validate_grid
from framework.tasks.arc_dataset import load_task
from framework.tasks.base import ArcTask, Verifier

Phase = Literal["explore", "test", "done"]


def normalize_query_grid(grid: Grid) -> Grid:
    return [
        [max(0, min(9, int(round(float(c))))) for c in row]
        for row in grid
    ]


def _ordered_verifier_chain(
    primary: VerifierSlot,
    valid: List[Tuple[VerifierSlot, Verifier]],
) -> List[Tuple[VerifierSlot, Verifier]]:
    first = [(s, f) for s, f in valid if s == primary]
    rest = [(s, f) for s, f in valid if s != primary]
    return first + rest


def _run_verifier_chain(
    inp: Grid,
    primary: VerifierSlot,
    valid: List[Tuple[VerifierSlot, Verifier]],
) -> Tuple[Grid, VerifierSlot]:
    errors: List[str] = []
    for slot, vfn in _ordered_verifier_chain(primary, valid):
        try:
            out = vfn(copy.deepcopy(inp))
            return clone_grid(out), slot
        except Exception as e:
            errors.append(f"{slot}: {type(e).__name__}: {e}")
    raise RuntimeError(
        "Every verifier failed on this input:\n" + "\n".join(errors)
    )


@dataclass
class ActiveArcTrialSession:
    """One interactive trial: explore with queries, then test on a dynamic pair."""

    task_id: str
    task: ArcTask
    seed: int
    rng: random.Random
    verifier_slot: VerifierSlot
    valid_verifiers: List[Tuple[VerifierSlot, Verifier]]
    hot_start_pair: Optional[GridPair]
    test_pair: GridPair
    dataset: str = "arc"
    phase: Phase = "explore"
    query_count: int = 0
    history: List[Dict[str, Any]] = field(default_factory=list)
    noise_probability: float = 0.0
    noisy_science: bool = False
    re_trials: bool = False
    hot_start: bool = False
    test_correct: Optional[bool] = None

    def train_pairs_json(self) -> List[Dict[str, List[List[int]]]]:
        """Canonical ARC training pairs (for prompts)."""
        out: List[Dict[str, List[List[int]]]] = []
        for p in self.task.train_pairs:
            out.append(
                {
                    "input": clone_grid(p.input),
                    "output": clone_grid(p.output),
                }
            )
        return out

    def hot_start_json(self) -> Optional[Dict[str, List[List[int]]]]:
        if self.hot_start_pair is None:
            return None
        hp = self.hot_start_pair
        return {
            "input": clone_grid(hp.input),
            "output": clone_grid(hp.output),
        }

    def submit_query(self, grid: Grid) -> Dict[str, Any]:
        """Exploration only: run verifier (+ optional noise), increment score on success."""
        if self.phase != "explore":
            return {
                "ok": False,
                "error": f"submit_query is only valid in explore phase (now: {self.phase}).",
            }
        try:
            inp = normalize_query_grid(clone_grid(grid))
            validate_grid(inp)
        except ValueError as e:
            return {"ok": False, "error": f"Invalid grid: {e}"}

        try:
            gold, used_slot = _run_verifier_chain(
                inp, self.verifier_slot, self.valid_verifiers
            )
        except RuntimeError as e:
            return {"ok": False, "error": str(e)}

        shown = clone_grid(gold)
        note = "(exact)"
        if self.noisy_science:
            try:
                shown, corrupted, kind = maybe_corrupt_query_output(
                    self.task_id,
                    self.task,
                    used_slot,
                    inp,
                    gold,
                    self.rng,
                    noise_probability=self.noise_probability,
                )
                note = f"(noisy: {kind})" if corrupted else "(exact)"
            except Exception as e:
                return {
                    "ok": False,
                    "error": f"Could not prepare noisy output: {type(e).__name__}: {e}",
                }

        self.query_count += 1
        self.history.append(
            {
                "input": clone_grid(inp),
                "output": clone_grid(shown),
                "note": note,
            }
        )
        return {
            "ok": True,
            "output_grid": clone_grid(shown),
            "note": note,
            "query_count": self.query_count,
        }

    def finish_exploration(self) -> Dict[str, Any]:
        """Switch to test phase; return the test input grid."""
        if self.phase != "explore":
            return {
                "ok": False,
                "error": f"finish_exploration only from explore (now: {self.phase}).",
            }
        self.phase = "test"
        ti = clone_grid(self.test_pair.input)
        return {
            "ok": True,
            "test_input_grid": ti,
            "phase": self.phase,
            "message": "Predict the output for test_input_grid using the same rule as in training.",
        }

    def submit_final_answer(self, grid: Grid) -> Dict[str, Any]:
        """Score against verifier on the test input."""
        if self.phase != "test":
            return {
                "ok": False,
                "error": f"submit_final_answer only in test phase (now: {self.phase}).",
            }
        ti = clone_grid(self.test_pair.input)
        try:
            pred = normalize_query_grid(clone_grid(grid))
            validate_grid(pred)
        except ValueError as e:
            return {"ok": False, "error": str(e)}

        try:
            gold, _slot = _run_verifier_chain(
                ti, self.verifier_slot, self.valid_verifiers
            )
        except RuntimeError as e:
            return {"ok": False, "error": f"Scoring failed: {e}"}

        ok = is_equal_grid(pred, gold)
        if self.re_trials and not ok:
            self.query_count += 10
            self.phase = "explore"
            self.test_correct = None
            return {
                "ok": True,
                "correct": False,
                "query_count": self.query_count,
                "phase": self.phase,
                "penalty_applied": True,
                "message": "Wrong answer: +10 query penalty. You are back in explore; query again, then finish_exploration to retry the same test.",
            }

        self.test_correct = ok
        self.phase = "done"
        return {
            "ok": True,
            "correct": ok,
            "query_count": self.query_count,
            "phase": self.phase,
            "done": True,
        }


def _create_conceptarc_trial_inputs(
    rng: random.Random,
    task_id: Optional[str],
) -> Tuple[
    str,
    ArcTask,
    VerifierSlot,
    Verifier,
    GridPair,
    List[Tuple[VerifierSlot, Verifier]],
]:
    """Pick a ConceptARC task + verifier + dynamic test pair (kept separate from ARC-AGI)."""
    from framework.integrations.conceptarc_adapter import (
        conceptarc_available,
        list_conceptarc_task_ids,
        load_conceptarc_task,
    )

    if not conceptarc_available():
        raise RuntimeError(
            "ConceptARC dataset unavailable: exported programs or the "
            "ConceptARC-GEN package could not be found. See "
            "framework/integrations/conceptarc_adapter.py."
        )

    def _fallback_test_pair(t: ArcTask, fn: Verifier) -> Optional[GridPair]:
        """Use a held-out exported test example when the live generator can't sample one."""
        n = min(len(t.test_inputs), len(t.test_outputs))
        order = list(range(n))
        rng.shuffle(order)
        for i in order:
            inp = t.test_inputs[i]
            try:
                if is_equal_grid(fn(copy.deepcopy(inp)), t.test_outputs[i]):
                    return GridPair(copy.deepcopy(inp), copy.deepcopy(t.test_outputs[i]))
            except Exception:
                continue
        return None

    def _build(t: ArcTask) -> Optional[
        Tuple[str, ArcTask, VerifierSlot, Verifier, GridPair, List[Tuple[VerifierSlot, Verifier]]]
    ]:
        fn = t.quinary_verifier or t.verifier
        if fn is None:
            return None
        valid: List[Tuple[VerifierSlot, Verifier]] = [("custom", fn)]
        tp = sample_consistent_dynamic_pair(t, fn, rng)
        if tp is None:
            tp = _fallback_test_pair(t, fn)
        if tp is None:
            return None
        return t.task_id, t, "custom", fn, tp, valid

    if task_id is not None:
        task = load_conceptarc_task(task_id)
        built = _build(task)
        if built is None:
            raise ValueError(
                f"Could not build a ConceptARC trial for {task_id!r}; try another seed."
            )
        return built

    ids = list(list_conceptarc_task_ids())
    if not ids:
        raise RuntimeError("No exported ConceptARC programs found.")
    rng.shuffle(ids)
    for cand in ids:
        try:
            task = load_conceptarc_task(cand)
        except Exception:
            continue
        built = _build(task)
        if built is not None:
            return built
    raise RuntimeError("Could not build a ConceptARC trial from any exported program.")


def create_trial_session(
    *,
    seed: int,
    task_id: Optional[str] = None,
    hot_start: bool = False,
    noisy_science: bool = False,
    re_trials: bool = False,
    noise_probability: float = 0.12,
    dataset: str = "arc",
) -> ActiveArcTrialSession:
    """Build a trial matching the Streamlit app (random eligible task or fixed ``task_id``).

    ``dataset`` selects the task pool: ``"arc"`` (default, ARC-AGI original) or
    ``"conceptarc"`` (ConceptARC DSL programs, kept fully separate).
    """
    rng = random.Random(seed)
    noise_p = float(noise_probability)
    if noisy_science:
        noise_p = max(0.05, min(0.20, noise_p))
    else:
        noise_p = 0.0

    tid: Optional[str] = None
    task: Optional[ArcTask] = None
    slot: Optional[VerifierSlot] = None
    verifier: Optional[Verifier] = None
    test_pair: Optional[GridPair] = None

    valid_list: Optional[List[Tuple[VerifierSlot, Verifier]]] = None

    if dataset == "conceptarc":
        tid, task, slot, verifier, test_pair, valid_list = _create_conceptarc_trial_inputs(
            rng, task_id
        )
    elif task_id is not None:
        task = load_task(task_id, load_alternative_verifiers=False)
        valid = list_valid_verifiers(task)
        if not valid:
            raise ValueError(f"No valid verifier for task {task_id!r}")
        slot, verifier = rng.choice(valid)
        tp = sample_consistent_dynamic_pair(task, verifier, rng)
        if tp is None:
            raise ValueError(
                f"Could not sample ARC-GEN dynamic test pair for {task_id!r}; try another seed."
            )
        tid = task_id
        test_pair = tp
        valid_list = valid
    else:
        for t_id, t in iter_eligible_tasks(rng):
            valid = list_valid_verifiers(t)
            if not valid:
                continue
            sl, ver = rng.choice(valid)
            tp = sample_consistent_dynamic_pair(t, ver, rng)
            if tp is None:
                continue
            tid, task, slot, verifier, test_pair = t_id, t, sl, ver, tp
            valid_list = valid
            break

    if (
        tid is None
        or task is None
        or slot is None
        or verifier is None
        or test_pair is None
        or valid_list is None
    ):
        raise RuntimeError(
            "Could not build trial (need eligible task + dynamic pair). "
            "Try --task-id or check external data."
        )

    hot: Optional[GridPair] = None
    if hot_start and task.train_pairs:
        hot = copy.deepcopy(rng.choice(task.train_pairs))

    return ActiveArcTrialSession(
        task_id=tid,
        task=task,
        seed=seed,
        rng=rng,
        verifier_slot=slot,
        valid_verifiers=valid_list,
        hot_start_pair=hot,
        test_pair=test_pair,
        dataset=dataset,
        phase="explore",
        query_count=0,
        history=[],
        noise_probability=noise_p,
        noisy_science=noisy_science,
        re_trials=re_trials,
        hot_start=hot_start,
        test_correct=None,
    )
