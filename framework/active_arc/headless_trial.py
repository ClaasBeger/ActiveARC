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
    test_pair: Optional[GridPair]
    dataset: str = "arc"
    phase: Phase = "explore"
    query_count: int = 0
    history: List[Dict[str, Any]] = field(default_factory=list)
    noise_probability: float = 0.0
    noisy_science: bool = False
    re_trials: bool = False
    hot_start: bool = False
    fixed_test: bool = False
    test_round: int = 0
    test_correct: Optional[bool] = None
    shown_test_inputs: List[Tuple[int, Grid]] = field(default_factory=list)
    test_input_query_count: int = 0

    def _matching_shown_test_round(self, grid: Grid) -> Optional[int]:
        for rnd, test_in in self.shown_test_inputs:
            if is_equal_grid(grid, test_in):
                return rnd
        return None

    def _verifier_fn(self) -> Verifier:
        for slot, fn in self.valid_verifiers:
            if slot == self.verifier_slot:
                return fn
        raise RuntimeError(f"No verifier callable for slot {self.verifier_slot!r}")

    def _sample_test_pair(self) -> Optional[GridPair]:
        exclude: List[Grid] = []
        if self.hot_start_pair is not None:
            exclude.append(self.hot_start_pair.input)
        for _, test_in in self.shown_test_inputs:
            exclude.append(test_in)
        pair = sample_consistent_dynamic_pair(
            self.task,
            self._verifier_fn(),
            self.rng,
            exclude_inputs=exclude or None,
        )
        return pair

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
        matched_test_round = self._matching_shown_test_round(inp)
        if matched_test_round is not None:
            self.test_input_query_count += 1
        self.history.append(
            {
                "input": clone_grid(inp),
                "output": clone_grid(shown),
                "note": note,
                "queried_shown_test_input": matched_test_round is not None,
                "matched_test_round": matched_test_round,
            }
        )
        out: Dict[str, Any] = {
            "ok": True,
            "output_grid": clone_grid(shown),
            "note": note,
            "query_count": self.query_count,
        }
        if matched_test_round is not None:
            out["queried_shown_test_input"] = True
            out["matched_test_round"] = matched_test_round
        return out

    def finish_exploration(self) -> Dict[str, Any]:
        """Switch to test phase; return the test input grid."""
        if self.phase != "explore":
            return {
                "ok": False,
                "error": f"finish_exploration only from explore (now: {self.phase}).",
            }
        if not self.fixed_test or self.test_pair is None:
            exclude_count = len(self.shown_test_inputs) + (
                1 if self.hot_start_pair is not None else 0
            )
            sampled = self._sample_test_pair()
            if sampled is None:
                return {
                    "ok": False,
                    "sampler_exhausted": True,
                    "message": (
                        f"Could not sample a new dynamic test pair for {self.task_id!r} "
                        f"(distinct from {exclude_count} prior example(s))."
                    ),
                    "phase": self.phase,
                    "query_count": self.query_count,
                }
            self.test_pair = sampled
            self.test_round += 1
        self.phase = "test"
        assert self.test_pair is not None
        ti = clone_grid(self.test_pair.input)
        self.shown_test_inputs.append((self.test_round, clone_grid(ti)))
        return {
            "ok": True,
            "test_input_grid": ti,
            "phase": self.phase,
            "test_round": self.test_round,
            "message": (
                "Testing stage. Apply the same transformation rule to test_input_grid and "
                "submit your predicted output grid with submit_final_answer "
                "(JSON array of rows; each cell an integer 0–9)."
            ),
        }

    def submit_final_answer(self, grid: Grid) -> Dict[str, Any]:
        """Score against verifier on the test input."""
        if self.phase != "test":
            return {
                "ok": False,
                "error": f"submit_final_answer only in test phase (now: {self.phase}).",
            }
        if self.test_pair is None:
            return {"ok": False, "error": "No test sample; call finish_exploration first."}
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
            retry_msg = (
                "Wrong answer: +10 query penalty. You are back in explore; query again, "
                "then finish_exploration to retry the same test."
                if self.fixed_test
                else "Wrong answer: +10 query penalty. You are back in explore; query again, "
                "then finish_exploration for a new test sample."
            )
            return {
                "ok": True,
                "correct": False,
                "query_count": self.query_count,
                "phase": self.phase,
                "penalty_applied": True,
                "message": retry_msg,
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


def _create_parc_trial_inputs(
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
    """Pick a P-ARC task + verifier + dynamic/stable test pair."""
    from framework.tasks.parc_dataset import (
        list_parc_task_ids,
        load_parc_task,
        parc_available,
    )

    if not parc_available():
        raise RuntimeError(
            "P-ARC dataset unavailable: data not found. Set PARC_ROOT/TEST2_DIR "
            "or keep the sibling PotARCin/PotARCin/Test2 checkout "
            "(see framework/tasks/parc_dataset.py)."
        )

    def _fallback_stable_or_test(t: ArcTask, fn: Verifier) -> Optional[GridPair]:
        pools: List[GridPair] = []
        if t.p_arc_stable_pairs:
            pools.extend(t.p_arc_stable_pairs)
        n = min(len(t.test_inputs), len(t.test_outputs))
        for i in range(n):
            pools.append(GridPair(t.test_inputs[i], t.test_outputs[i]))
        order = list(range(len(pools)))
        rng.shuffle(order)
        for i in order:
            pair = pools[i]
            try:
                if is_equal_grid(fn(copy.deepcopy(pair.input)), pair.output):
                    return GridPair(copy.deepcopy(pair.input), copy.deepcopy(pair.output))
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
            tp = _fallback_stable_or_test(t, fn)
        if tp is None:
            return None
        return t.task_id, t, "custom", fn, tp, valid

    if task_id is not None:
        task = load_parc_task(task_id)
        built = _build(task)
        if built is None:
            raise ValueError(
                f"Could not build a P-ARC trial for {task_id!r}; try another seed."
            )
        return built

    ids = list(list_parc_task_ids())
    if not ids:
        raise RuntimeError("No P-ARC tasks found.")
    rng.shuffle(ids)
    for cand in ids:
        try:
            task = load_parc_task(cand)
        except Exception:
            continue
        built = _build(task)
        if built is not None:
            return built
    raise RuntimeError("Could not build a P-ARC trial from any available task.")


def _create_conceptarc_trial_inputs(
    rng: random.Random,
    task_id: Optional[str],
    *,
    sample_family: bool = False,
    persist_sampled_family: bool = False,
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
        concept_from_sample_request,
        conceptarc_available,
        is_conceptarc_sample_request,
        list_conceptarc_task_ids,
        load_conceptarc_task,
        sample_conceptarc_task,
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

    want_sample = sample_family or is_conceptarc_sample_request(task_id)
    if want_sample:
        concept = (
            concept_from_sample_request(task_id)
            if task_id is not None and is_conceptarc_sample_request(task_id)
            else None
        )
        task = sample_conceptarc_task(
            concept=concept,
            seed=rng.randint(1, 2**31 - 1),
            persist=persist_sampled_family,
        )
        built = _build(task)
        if built is None:
            raise ValueError(
                "Could not build a ConceptARC trial from a newly sampled family; "
                "try another seed."
            )
        return built

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


def _sample_hot_start_pair(
    task: ArcTask,
    verifier: Verifier,
    rng: random.Random,
    *,
    hot_start: bool,
) -> Optional[GridPair]:
    if not hot_start:
        return None
    if task.arc_gen_generator is not None:
        hot = sample_consistent_dynamic_pair(task, verifier, rng)
        if hot is None:
            raise ValueError(
                f"Could not sample dynamic hot-start pair for {task.task_id!r}; try another seed."
            )
        return hot
    if task.train_pairs:
        return copy.deepcopy(rng.choice(task.train_pairs))
    return None


def _sample_hot_and_test_pairs(
    task: ArcTask,
    verifier: Verifier,
    rng: random.Random,
    *,
    hot_start: bool,
) -> Tuple[Optional[GridPair], GridPair]:
    """Sample dynamic hot-start (optional) and a fixed test pair from the generator."""
    if task.arc_gen_generator is None:
        raise ValueError(f"Task {task.task_id!r} has no dynamic generator")

    hot = _sample_hot_start_pair(task, verifier, rng, hot_start=hot_start)
    exclude: List[Grid] = [hot.input] if hot is not None else []

    test = sample_consistent_dynamic_pair(
        task, verifier, rng, exclude_inputs=exclude or None
    )
    if test is None:
        detail = " (distinct from hot-start)" if hot is not None else ""
        raise ValueError(
            f"Could not sample dynamic test pair for {task.task_id!r}{detail}; try another seed."
        )
    return hot, test


def _resolve_hot_start_pair(
    task: ArcTask,
    verifier: Verifier,
    rng: random.Random,
    test_pair: GridPair,
    *,
    hot_start: bool,
) -> Tuple[Optional[GridPair], GridPair]:
    """Attach a hot-start pair; resample test if it collides with hot-start."""
    if not hot_start:
        return None, test_pair

    if task.arc_gen_generator is not None:
        hot = sample_consistent_dynamic_pair(task, verifier, rng)
        if hot is None:
            raise ValueError(
                f"Could not sample dynamic hot-start pair for {task.task_id!r}; try another seed."
            )
        if is_equal_grid(test_pair.input, hot.input):
            replacement = sample_consistent_dynamic_pair(
                task, verifier, rng, exclude_inputs=[hot.input]
            )
            if replacement is None:
                raise ValueError(
                    f"Could not sample test pair distinct from hot-start for {task.task_id!r}; "
                    "try another seed."
                )
            test_pair = replacement
        return hot, test_pair

    if task.train_pairs:
        return copy.deepcopy(rng.choice(task.train_pairs)), test_pair

    return None, test_pair


def create_trial_session(
    *,
    seed: int,
    task_id: Optional[str] = None,
    hot_start: bool = True,
    noisy_science: bool = False,
    re_trials: bool = True,
    fixed_test: bool = False,
    noise_probability: float = 0.12,
    dataset: str = "arc",
    sample_family: bool = False,
    persist_sampled_family: bool = False,
) -> ActiveArcTrialSession:
    """Build a trial matching the Streamlit app (random eligible task or fixed ``task_id``).

    ``dataset`` selects the task pool: ``"arc"`` (default, ARC-AGI original),
    ``"conceptarc"`` (ConceptARC DSL programs), or ``"parc"`` (P-ARC).

    For ConceptARC, ``sample_family=True`` or ``task_id`` of the form ``sample``,
    ``sample/<concept>``, or ``<concept>/sample`` invents a new DSL task family
    online. ``persist_sampled_family`` writes that family into the exported
    program catalog (and ConceptARC-GEN specs).
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
    hot: Optional[GridPair] = None

    if dataset == "conceptarc":
        tid, task, slot, verifier, test_pair, valid_list = _create_conceptarc_trial_inputs(
            rng,
            task_id,
            sample_family=sample_family,
            persist_sampled_family=persist_sampled_family,
        )
    elif dataset == "parc":
        tid, task, slot, verifier, test_pair, valid_list = _create_parc_trial_inputs(
            rng, task_id
        )
    elif task_id is not None:
        task = load_task(task_id, load_alternative_verifiers=False)
        valid = list_valid_verifiers(task)
        if not valid:
            raise ValueError(f"No valid verifier for task {task_id!r}")
        slot, verifier = rng.choice(valid)
        hot = _sample_hot_start_pair(task, verifier, rng, hot_start=hot_start)
        if fixed_test:
            exclude = [hot.input] if hot is not None else []
            test_pair = sample_consistent_dynamic_pair(
                task, verifier, rng, exclude_inputs=exclude or None
            )
            if test_pair is None:
                raise ValueError(
                    f"Could not sample dynamic test pair for {task_id!r}; try another seed."
                )
        else:
            test_pair = None
        tid = task_id
        valid_list = valid
    else:
        for t_id, t in iter_eligible_tasks(rng):
            valid = list_valid_verifiers(t)
            if not valid:
                continue
            sl, ver = rng.choice(valid)
            try:
                hot = _sample_hot_start_pair(t, ver, rng, hot_start=hot_start)
                if fixed_test:
                    exclude = [hot.input] if hot is not None else []
                    tp = sample_consistent_dynamic_pair(
                        t, ver, rng, exclude_inputs=exclude or None
                    )
                    if tp is None:
                        continue
                else:
                    tp = None
            except ValueError:
                continue
            tid, task, slot, verifier, test_pair = t_id, t, sl, ver, tp
            valid_list = valid
            break

    if (
        tid is None
        or task is None
        or slot is None
        or verifier is None
        or valid_list is None
        or (fixed_test and test_pair is None)
    ):
        raise RuntimeError(
            "Could not build trial (need eligible task + dynamic pair). "
            "Try --task-id or check external data."
        )

    if dataset in ("conceptarc", "parc"):
        assert test_pair is not None
        hot, resolved_test = _resolve_hot_start_pair(
            task, verifier, rng, test_pair, hot_start=hot_start
        )
        test_pair = resolved_test if fixed_test else None

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
        fixed_test=fixed_test,
        test_correct=None,
    )
