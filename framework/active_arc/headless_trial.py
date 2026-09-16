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
    pick_verifier,
    sample_consistent_dynamic_pair,
)
from framework.dimensions.classification_distribution import VerifierSlot
from framework.grids import Grid, GridPair, clone_grid, is_equal_grid, validate_grid
from framework.tasks.arc_dataset import load_task
from framework.tasks.base import ArcTask, Verifier

Phase = Literal["explore", "test", "done"]

# Model-facing message for malformed inputs / out-of-domain queries.
# Never include verifier exception text — that leaks rule structure.
INVALID_INPUT_OR_RULE_MESSAGE = "Invalid Input Grid or Rule not Applicable"



def malformed_grid_message(grid: Any) -> Optional[str]:
    """Say what is wrong with the *shape* of a submitted grid, or None if it is fine.

    The generic INVALID_INPUT_OR_RULE_MESSAGE is deliberately vague because it
    also covers a verifier refusing a query, and saying why would leak the rule.
    The shape of the grid the model just wrote leaks nothing, so describing it
    costs nothing and saves a turn: a model told "rows have widths 9, 10, 11"
    can fix that, where one told "invalid input" usually submits the same grid
    again. Luna lost roughly a third of its turns this way.
    """
    if not isinstance(grid, list) or not grid:
        return "Grid must be a non-empty list of rows."
    if not all(isinstance(r, list) for r in grid):
        return "Grid must be a list of rows, each row a list of integers."
    widths = sorted({len(r) for r in grid})
    if widths == [0]:
        return "Grid rows must be non-empty."
    if len(widths) > 1:
        return (
            "Grid must be rectangular: every row needs the same number of cells, "
            f"but the rows have widths {', '.join(str(w) for w in widths)}. "
            "Re-send the grid with all rows the same length."
        )
    for row in grid:
        for cell in row:
            if isinstance(cell, bool) or not isinstance(cell, int):
                return f"Grid cells must be integers 0-9; found {cell!r}."
            if not 0 <= cell <= 9:
                return f"Grid cells must be integers 0-9; found {cell}."
    return None


def normalize_query_grid(grid: Grid) -> Grid:
    return [
        [max(0, min(9, int(round(float(c))))) for c in row]
        for row in grid
    ]


def _is_answer_grid(grid: Any) -> bool:
    """Whether this is a real answer: a rectangle of colours and nothing else."""
    if not isinstance(grid, list) or not grid:
        return False
    width = len(grid[0]) if isinstance(grid[0], list) else -1
    if width <= 0:
        return False
    for row in grid:
        if not isinstance(row, list) or len(row) != width:
            return False
        for cell in row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                return False
    return True


def _run_trial_verifier(inp: Grid, verifier: Verifier) -> Grid:
    """Run the trial's pinned verifier. Raises ``RuntimeError`` if it fails.

    Only this one verifier ever answers, so every query, hot-start pair, test
    sample and answer check in a trial comes from the same rule; falling back to
    another valid slot would silently mix rules within a session.

    A verifier that raises is easy to spot. The harder case is one that returns
    something that is not a grid at all -- a cell of ``None``, or a value like 11
    -- which some slots do when a query falls outside the shapes they were
    written against. That is not an answer, so it is treated as a failure rather
    than shown to the model.
    """
    try:
        out = verifier(copy.deepcopy(inp))
    except Exception as e:
        raise RuntimeError(f"Trial verifier failed: {type(e).__name__}: {e}") from e
    if not _is_answer_grid(out):
        raise RuntimeError("Trial verifier returned something that is not a grid of colours")
    return clone_grid(out)


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
    # The one callable chosen for this trial. Pinned because a slot name is not a
    # unique key (ARC-AGI-2 exposes several verifiers under "custom").
    verifier: Optional[Verifier] = None
    # Program mode: the test stage asks for a Python rule implementation, scored on
    # train / test / generator-stable / generator-dynamic instead of one test grid.
    program_test: bool = False
    # Record the program without scoring it; score later with pipelines.score_programs.
    defer_program_eval: bool = False
    program_source: Optional[str] = None
    program_eval: Optional[Dict[str, Any]] = None
    dataset: str = "arc"
    phase: Phase = "explore"
    query_count: int = 0
    history: List[Dict[str, Any]] = field(default_factory=list)
    noise_probability: float = 0.0
    noisy_science: bool = False
    re_trials: bool = False
    wrong_answer_penalty: int = 0
    hot_start: bool = False
    fixed_test: bool = False
    test_round: int = 0
    test_correct: Optional[bool] = None
    shown_test_inputs: List[Tuple[int, Grid]] = field(default_factory=list)
    test_input_query_count: int = 0
    # Matched-K arm: the trial must end with exactly this many successful queries
    # before testing, so its evidence count matches the other arms. None = the
    # model decides when to stop, which is the free-interaction condition.
    forced_queries: Optional[int] = None
    # Which held-out items the test phase asks about: the trial's generator-sampled
    # pair, the task's own authored item(s), or both. All of them are shown at once
    # and answered in the exploration conversation, so the reasoning built up across
    # queries is still in hand -- which is the whole point of an active trial.
    test_source: str = "sampled"
    test_items: List[Tuple[Grid, Grid]] = field(default_factory=list)
    test_item_correct: List[bool] = field(default_factory=list)
    test_item_kinds: List[str] = field(default_factory=list)

    def remaining_forced_queries(self) -> Optional[int]:
        if self.forced_queries is None:
            return None
        return max(0, self.forced_queries - self.query_count)

    def _matching_shown_test_round(self, grid: Grid) -> Optional[int]:
        for rnd, test_in in self.shown_test_inputs:
            if is_equal_grid(grid, test_in):
                return rnd
        return None

    def _verifier_fn(self) -> Verifier:
        if self.verifier is not None:
            return self.verifier
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

    def announced_wrong_answer_penalty(self) -> int:
        """Query-count penalty announced in the prompt and applied on a wrong test.

        Explicit ``wrong_answer_penalty`` wins. Re-trials with no override keep +10.
        """
        if self.wrong_answer_penalty > 0:
            return int(self.wrong_answer_penalty)
        if self.re_trials:
            return 10
        return 0

    def hot_start_json(self) -> Optional[Dict[str, List[List[int]]]]:
        if self.hot_start_pair is None:
            return None
        hp = self.hot_start_pair
        return {
            "input": clone_grid(hp.input),
            "output": clone_grid(hp.output),
        }

    def evidence_pairs_json(self) -> List[Dict[str, List[List[int]]]]:
        """Every pair the model actually saw: the hot start, then its query results.

        Outputs are the *shown* ones, so under ``--noisy-science`` the evidence
        carries the same corruption the model reasoned from rather than the
        gold answer it never saw.
        """
        pairs: List[Dict[str, List[List[int]]]] = []
        hot = self.hot_start_json()
        if hot is not None:
            pairs.append(hot)
        for item in self.history:
            pairs.append(
                {
                    "input": clone_grid(item["input"]),
                    "output": clone_grid(item["output"]),
                }
            )
        return pairs

    def official_test_items(self) -> List[Tuple[Grid, Grid]]:
        """The task's own held-out items, which the static arm is scored on."""
        n = min(len(self.task.test_inputs), len(self.task.test_outputs))
        return [
            (clone_grid(self.task.test_inputs[i]), clone_grid(self.task.test_outputs[i]))
            for i in range(n)
        ]

    def submit_query(self, grid: Grid) -> Dict[str, Any]:
        """Exploration only: run verifier (+ optional noise), increment score on success."""
        remaining = self.remaining_forced_queries()
        if remaining == 0 and self.phase == "explore":
            return {
                "ok": False,
                "error": (
                    f"Query budget spent ({self.forced_queries} of "
                    f"{self.forced_queries}). Call request_test now."
                ),
                "queries_remaining": 0,
            }
        if self.phase != "explore":
            return {
                "ok": False,
                "error": f"submit_query is only valid in explore phase (now: {self.phase}).",
            }
        shape_error = malformed_grid_message(grid)
        if shape_error is not None:
            return {"ok": False, "error": shape_error, "malformed_grid": True}
        try:
            inp = normalize_query_grid(clone_grid(grid))
            validate_grid(inp)
        except ValueError:
            return {"ok": False, "error": INVALID_INPUT_OR_RULE_MESSAGE}

        try:
            gold = _run_trial_verifier(inp, self._verifier_fn())
        except RuntimeError:
            return {"ok": False, "error": INVALID_INPUT_OR_RULE_MESSAGE}

        shown = clone_grid(gold)
        note = "(exact)"
        if self.noisy_science:
            try:
                shown, corrupted, kind = maybe_corrupt_query_output(
                    self.task_id,
                    self.task,
                    self.verifier_slot,
                    inp,
                    gold,
                    self.rng,
                    noise_probability=self.noise_probability,
                )
                note = f"(noisy: {kind})" if corrupted else "(exact)"
            except Exception:
                return {"ok": False, "error": INVALID_INPUT_OR_RULE_MESSAGE}

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
        """Switch to test phase; return the test input grid (``request_test`` tool)."""
        if self.phase != "explore":
            return {
                "ok": False,
                "error": f"request_test only from explore (now: {self.phase}).",
            }
        remaining = self.remaining_forced_queries()
        if remaining:
            return {
                "ok": False,
                "error": (
                    f"{remaining} more quer{'y' if remaining == 1 else 'ies'} must be "
                    f"submitted before testing ({self.query_count} of "
                    f"{self.forced_queries} used). Call submit_query."
                ),
                "queries_remaining": remaining,
            }
        if self.program_test:
            self.phase = "test"
            self.test_round += 1
            return {
                "ok": True,
                "phase": self.phase,
                "test_round": self.test_round,
                "message": (
                    "Testing stage. Submit a Python program implementing the rule with "
                    "submit_program. It must define transform(grid) taking a grid "
                    "(list of rows of ints 0-9) and returning the transformed grid. "
                    "It is scored on held-out examples, not on a single test input."
                ),
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
                        "Could not sample a new dynamic test pair "
                        f"(distinct from {exclude_count} prior example(s))."
                    ),
                    "phase": self.phase,
                    "query_count": self.query_count,
                }
            self.test_pair = sampled
            self.test_round += 1
        self.phase = "test"
        assert self.test_pair is not None

        items: List[Tuple[Grid, Grid]] = []
        kinds: List[str] = []
        if self.test_source in ("official", "both"):
            for oi, oo in self.official_test_items():
                items.append((oi, oo))
                kinds.append("official")
        if self.test_source in ("sampled", "both"):
            items.append((clone_grid(self.test_pair.input), clone_grid(self.test_pair.output)))
            kinds.append("sampled")
        if not items:
            items = [(clone_grid(self.test_pair.input), clone_grid(self.test_pair.output))]
            kinds = ["sampled"]
        self.test_items = items
        self.test_item_kinds = kinds
        self.test_item_correct = []
        for ti_grid, _ in items:
            self.shown_test_inputs.append((self.test_round, clone_grid(ti_grid)))

        # The grids are not handed over here. Each is asked on its own branch of
        # the exploration conversation, so one item can never be in context while
        # another is answered; the loop drives that.
        return {
            "ok": True,
            "phase": self.phase,
            "test_round": self.test_round,
            "n_test_items": len(items),
            "message": (
                f"Testing stage. You will be given {len(items)} test input"
                f"{'' if len(items) == 1 else 's'}"
                + ("" if len(items) == 1 else ", one at a time and answered separately")
                + ". Apply the same transformation rule to each and submit the "
                "predicted output grid with submit_final_answer."
            ),
        }

    def submit_program(self, code: Any) -> Dict[str, Any]:
        """Program mode: score a submitted rule implementation on the standard sets."""
        if not self.program_test:
            return {
                "ok": False,
                "error": "submit_program is only valid in program-test trials.",
            }
        if self.phase != "test":
            return {
                "ok": False,
                "error": f"submit_program only in test phase (now: {self.phase}).",
            }
        if not isinstance(code, str) or not code.strip():
            return {"ok": False, "error": "Missing or empty program source."}

        if self.defer_program_eval:
            # Store only. No correctness is computed, so nothing is revealed to the
            # model and re-trials have nothing to retry on: the trial ends here.
            self.program_source = code
            self.program_eval = None
            self.test_correct = None
            self.phase = "done"
            return {
                "ok": True,
                "recorded": True,
                "query_count": self.query_count,
                "phase": self.phase,
                "done": True,
                "message": "Program received. The trial is complete.",
            }

        from framework.active_arc.program_eval import evaluate_program

        report = evaluate_program(self.task, code, rng=self.rng)
        self.program_source = code
        self.program_eval = report.to_dict()
        # A program that does not compile or exposes no entry point is simply a
        # wrong solution: scored, not retried.
        ok = report.all_correct

        penalty = self.announced_wrong_answer_penalty()
        if not ok and penalty > 0:
            self.query_count += penalty
        set_scores = {
            name: f"{s['n_correct']}/{s['n']}"
            for name, s in (self.program_eval.get("sets") or {}).items()
        }
        load_error = None if report.loaded else report.error
        if self.re_trials and not ok:
            self.phase = "explore"
            self.test_correct = None
            retry: Dict[str, Any] = {
                "ok": True,
                "correct": False,
                "set_scores": set_scores,
                "query_count": self.query_count,
                "phase": self.phase,
                "penalty_applied": True,
                "penalty": penalty,
                "message": (
                    f"Program did not reproduce every example (+{penalty} query penalty). "
                    "You are back in explore; query again, then request_test to retry."
                ),
            }
            if load_error:
                retry["load_error"] = load_error
            return retry

        self.test_correct = ok
        self.phase = "done"
        out: Dict[str, Any] = {
            "ok": True,
            "correct": ok,
            "set_scores": set_scores,
            "query_count": self.query_count,
            "phase": self.phase,
            "done": True,
        }
        if not ok and penalty > 0:
            out["penalty_applied"] = True
            out["penalty"] = penalty
        if load_error:
            out["load_error"] = load_error
        return out

    def submit_final_answer(self, grid: Any = None, grids: Any = None) -> Dict[str, Any]:
        """Score the answer(s) for the item(s) the test phase asked about.

        A single-item trial keeps the original ``grid`` argument and behaviour.
        When several items were shown together, ``grids`` carries one answer per
        item in the order shown, and the trial is correct only if every one of
        them is -- the same all-or-nothing rule the static arm is scored by.
        """
        if self.program_test:
            return {
                "ok": False,
                "error": "This trial expects a program: use submit_program.",
            }
        if self.phase != "test":
            return {
                "ok": False,
                "error": f"submit_final_answer only in test phase (now: {self.phase}).",
            }
        if self.test_pair is None and not self.test_items:
            return {"ok": False, "error": "No test sample; call request_test first."}

        items = self.test_items or [
            (clone_grid(self.test_pair.input), clone_grid(self.test_pair.output))
        ]
        if len(items) > 1:
            answers = grids if grids is not None else grid
            if not isinstance(answers, list) or len(answers) != len(items):
                return {
                    "ok": False,
                    "error": (
                        f"This trial has {len(items)} test inputs: submit "
                        f'"grids" as a list of {len(items)} output grids, in the '
                        "order they were shown."
                    ),
                }
        else:
            answers = [grids[0] if isinstance(grids, list) and grids else grid]

        preds: List[Grid] = []
        for a in answers:
            shape_error = malformed_grid_message(a)
            if shape_error is not None:
                return {"ok": False, "error": shape_error, "malformed_grid": True}
            try:
                pred = normalize_query_grid(clone_grid(a))
                validate_grid(pred)
            except (ValueError, TypeError):
                return {"ok": False, "error": INVALID_INPUT_OR_RULE_MESSAGE}
            preds.append(pred)

        per_item: List[bool] = []
        for pred, (ti_grid, gold_out) in zip(preds, items):
            gold = gold_out
            if gold is None:
                try:
                    gold = _run_trial_verifier(ti_grid, self._verifier_fn())
                except RuntimeError:
                    return {"ok": False, "error": INVALID_INPUT_OR_RULE_MESSAGE}
            per_item.append(is_equal_grid(pred, gold))
        self.test_item_correct = per_item
        ok = all(per_item)
        penalty = self.announced_wrong_answer_penalty()
        if not ok and penalty > 0:
            self.query_count += penalty
        if self.re_trials and not ok:
            self.phase = "explore"
            self.test_correct = None
            retry_msg = (
                f"Wrong answer: +{penalty} query penalty. You are back in explore; query again, "
                "then request_test to retry the same test."
                if self.fixed_test
                else f"Wrong answer: +{penalty} query penalty. You are back in explore; query again, "
                "then request_test for a new test sample."
            )
            return {
                "ok": True,
                "correct": False,
                "query_count": self.query_count,
                "phase": self.phase,
                "penalty_applied": True,
                "penalty": penalty,
                "message": retry_msg,
            }

        self.test_correct = ok
        self.phase = "done"
        out: Dict[str, Any] = {
            "ok": True,
            "correct": ok,
            "query_count": self.query_count,
            "phase": self.phase,
            "done": True,
        }
        if not ok and penalty > 0:
            out["penalty_applied"] = True
            out["penalty"] = penalty
        return out


def _create_arc2_trial_inputs(
    rng: random.Random,
    task_id: Optional[str],
    *,
    hot_start: bool,
    fixed_test: bool,
) -> Tuple[
    str,
    ArcTask,
    VerifierSlot,
    Verifier,
    Optional[GridPair],
    List[Tuple[VerifierSlot, Verifier]],
    Optional[GridPair],
]:
    """Pick a validated ARC-AGI-2 task + verifier + optional hot-start pair."""
    from framework.integrations.agi2_verifiers import list_agi2_valid_task_ids

    ids = list(list_agi2_valid_task_ids())
    if not ids:
        raise RuntimeError(
            "No validated ARC-AGI-2 verifiers under external/agi2_verifiers/valid."
        )

    def _build(t: ArcTask) -> Optional[
        Tuple[
            str,
            ArcTask,
            VerifierSlot,
            Verifier,
            Optional[GridPair],
            List[Tuple[VerifierSlot, Verifier]],
            Optional[GridPair],
        ]
    ]:
        picked = pick_verifier(t, rng)
        if picked is None:
            return None
        valid = list_valid_verifiers(t)
        sl, ver = picked
        try:
            hot = _sample_hot_start_pair(t, ver, rng, hot_start=hot_start)
            if fixed_test:
                exclude = [hot.input] if hot is not None else []
                tp = sample_consistent_dynamic_pair(
                    t, ver, rng, exclude_inputs=exclude or None
                )
                if tp is None:
                    return None
            else:
                tp = None
        except ValueError:
            return None
        return t.task_id, t, sl, ver, tp, valid, hot

    if task_id is not None:
        if task_id not in ids:
            raise ValueError(
                f"Task {task_id!r} is not in the validated ARC-AGI-2 set "
                f"({len(ids)} tasks)."
            )
        task = load_task(task_id, load_alternative_verifiers=False)
        built = _build(task)
        if built is None:
            raise ValueError(
                f"Could not build an ARC-AGI-2 trial for {task_id!r}; try another seed."
            )
        return built

    order = ids[:]
    rng.shuffle(order)
    for cand in order:
        try:
            task = load_task(cand, load_alternative_verifiers=False)
        except Exception:
            continue
        built = _build(task)
        if built is not None:
            return built
    raise RuntimeError(
        "Could not build an ARC-AGI-2 trial from any validated task. "
        "Check external/agi2_verifiers/valid and ARC-GEN V2 generators."
    )


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


def _fallback_train_pair(
    task: ArcTask,
    verifier: Verifier,
    rng: random.Random,
) -> Optional[GridPair]:
    """Use an exported train example when the live generator cannot sample hot-start."""
    if not task.train_pairs:
        return None
    order = list(range(len(task.train_pairs)))
    rng.shuffle(order)
    for i in order:
        pair = task.train_pairs[i]
        try:
            if is_equal_grid(verifier(copy.deepcopy(pair.input)), pair.output):
                return copy.deepcopy(pair)
        except Exception:
            continue
    return None


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
            hot = _fallback_train_pair(task, verifier, rng)
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
            hot = _fallback_train_pair(task, verifier, rng)
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
    re_trials: bool = False,
    wrong_answer_penalty: int = 0,
    fixed_test: bool = False,
    noise_probability: float = 0.12,
    program_test: bool = False,
    defer_program_eval: bool = False,
    dataset: str = "arc",
    sample_family: bool = False,
    persist_sampled_family: bool = False,
    forced_queries: Optional[int] = None,
    test_source: str = "sampled",
) -> ActiveArcTrialSession:
    """Build a trial matching the Streamlit app (random eligible task or fixed ``task_id``).

    ``dataset`` selects the task pool: ``"arc"`` (default, ARC-AGI-1 training),
    ``"arc2"`` (validated ARC-AGI-2), ``"conceptarc"`` (ConceptARC DSL programs),
    or ``"parc"`` (P-ARC).

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
    elif dataset == "arc2":
        tid, task, slot, verifier, test_pair, valid_list, hot = _create_arc2_trial_inputs(
            rng, task_id, hot_start=hot_start, fixed_test=fixed_test
        )
    elif task_id is not None:
        task = load_task(task_id, load_alternative_verifiers=False)
        picked = pick_verifier(task, rng)
        if picked is None:
            raise ValueError(f"No valid verifier for task {task_id!r}")
        valid = list_valid_verifiers(task)
        slot, verifier = picked
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
            picked = pick_verifier(t, rng)
            if picked is None:
                continue
            valid = list_valid_verifiers(t)
            sl, ver = picked
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
        verifier=verifier,
        hot_start_pair=hot,
        test_pair=test_pair,
        dataset=dataset,
        phase="explore",
        query_count=0,
        history=[],
        noise_probability=noise_p,
        noisy_science=noisy_science,
        re_trials=re_trials,
        wrong_answer_penalty=max(0, int(wrong_answer_penalty)),
        hot_start=hot_start,
        fixed_test=fixed_test,
        program_test=program_test,
        defer_program_eval=defer_program_eval,
        test_correct=None,
        forced_queries=forced_queries,
        test_source=test_source,
    )
