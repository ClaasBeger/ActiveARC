"""Teacher/student state machine for Inverse Query Generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

from framework.active_arc.headless_trial import (
    INVALID_INPUT_OR_RULE_MESSAGE,
    ActiveArcTrialSession,
    _run_trial_verifier,
    create_trial_session,
    normalize_query_grid,
)
from framework.active_arc.verifier_selection import sample_consistent_dynamic_pair
from framework.grids import Grid, GridPair, clone_grid, is_equal_grid, validate_grid
from framework.inverse_query.sources import TaskPrograms, load_task_programs
from framework.tasks.base import Verifier

Phase = Literal["teach", "exam", "done"]

SHOW_EXAMPLE_SUCCESS_MESSAGE = "Demonstration provided to Student successfully."


def _parse_grid(grid: Any) -> Grid:
    if not isinstance(grid, list):
        raise ValueError("grid must be a JSON array of rows")
    out = normalize_query_grid(clone_grid(grid))
    validate_grid(out)
    return out


@dataclass
class InverseQuerySession:
    trial: ActiveArcTrialSession
    programs: TaskPrograms
    exam_n: int = 10
    include_teacher_sample: bool = True
    teacher_sample: Optional[GridPair] = None
    phase: Phase = "teach"
    demonstrations: List[GridPair] = field(default_factory=list)
    probes: List[Dict[str, Any]] = field(default_factory=list)
    exam_pairs: List[GridPair] = field(default_factory=list)
    exam_predictions: List[Optional[Grid]] = field(default_factory=list)
    exam_correct: List[Optional[bool]] = field(default_factory=list)
    exam_index: int = 0
    n_show_example: int = 0
    n_show_transformed: int = 0
    # Matched-K teaching: stop at exactly this many demonstrations so the set the
    # teacher hands over is the same size as the authored one the static arm gets.
    max_demonstrations: Optional[int] = None
    # Probing the student is off in the matched comparison: the ARC author who
    # wrote the authored demos could not question a particular learner either,
    # and the set is scored afterwards by a common evaluator, so adapting to one
    # student's replies would measure something else.
    allow_probes: bool = True
    n_query_student: int = 0
    n_failed_show: int = 0
    # Free lookups of the verifier's implementation (ConceptARC): logged, not scored.
    n_get_implementation: int = 0
    # Teacher sanity check: the exam is drawn before teaching and the teacher,
    # given its normal briefing, must solve every item; only then is the trial
    # worth the student's cost. The same items are used for the student.
    exam_predrawn: bool = False
    exam_replaced: int = 0
    teacher_exam_predictions: List[Optional[Grid]] = field(default_factory=list)
    teacher_exam_correct: List[Optional[bool]] = field(default_factory=list)
    teacher_exam_passed: Optional[bool] = None

    @property
    def task_id(self) -> str:
        return self.trial.task_id

    @property
    def dataset(self) -> str:
        return self.trial.dataset

    @property
    def seed(self) -> int:
        return self.trial.seed

    def _verifier(self) -> Verifier:
        for slot, fn in self.trial.valid_verifiers:
            if slot == self.trial.verifier_slot:
                return fn
        raise RuntimeError(f"No verifier callable for slot {self.trial.verifier_slot!r}")

    def _gold(self, inp: Grid) -> Grid:
        # The trial's pinned verifier answers every teacher probe and exam pair,
        # so one rule governs the whole session (no fallback to another slot).
        return _run_trial_verifier(inp, self._verifier())

    def _seen_inputs(self) -> List[Grid]:
        seen: List[Grid] = []
        if self.teacher_sample is not None:
            seen.append(clone_grid(self.teacher_sample.input))
        seen.extend(clone_grid(p.input) for p in self.demonstrations)
        for probe in self.probes:
            seen.append(clone_grid(probe["input"]))
        return seen

    def implementation_available(self) -> bool:
        """Whether the verifier's code is offered by tool rather than inline."""
        return self.programs.verifier_program_json is not None and bool(self.programs.verifier_source)

    def get_verifier_implementation(self) -> Dict[str, Any]:
        if not self.implementation_available():
            return {"ok": False, "error": "No separate implementation for this task; the briefing is complete."}
        self.n_get_implementation += 1
        src = self.programs.verifier_source or ""
        return {"ok": True, "implementation": src, "lines": src.count("\n") + 1}

    def teacher_sample_json(self) -> Optional[Dict[str, List[List[int]]]]:
        if self.teacher_sample is None:
            return None
        return {
            "input": clone_grid(self.teacher_sample.input),
            "output": clone_grid(self.teacher_sample.output),
        }

    def demonstrations_json(self) -> List[Dict[str, List[List[int]]]]:
        return [
            {"input": clone_grid(p.input), "output": clone_grid(p.output)}
            for p in self.demonstrations
        ]

    def _append_demo(self, pair: GridPair) -> None:
        self.demonstrations.append(
            GridPair(clone_grid(pair.input), clone_grid(pair.output))
        )

    def show_example(self, input_grid: Any, output_grid: Any) -> Dict[str, Any]:
        """Show an authored pair if it matches gold; otherwise return gold to the teacher."""
        if self.phase != "teach":
            return {"ok": False, "error": "show_example is only valid before the exam."}
        if (self.max_demonstrations is not None
                and len(self.demonstrations) >= self.max_demonstrations):
            return {
                "ok": False,
                "error": (
                    f"All {self.max_demonstrations} demonstrations have been shown. "
                    "The teaching set is complete."
                ),
                "budget_spent": True,
            }
        try:
            inp = _parse_grid(input_grid)
            pred = _parse_grid(output_grid)
        except ValueError:
            self.n_failed_show += 1
            return {"ok": False, "error": INVALID_INPUT_OR_RULE_MESSAGE}
        try:
            gold = self._gold(inp)
        except RuntimeError:
            self.n_failed_show += 1
            return {"ok": False, "error": INVALID_INPUT_OR_RULE_MESSAGE}
        if is_equal_grid(pred, gold):
            self._append_demo(GridPair(inp, gold))
            self.n_show_example += 1
            return {
                "ok": True,
                "shown_to_student": True,
                "message": SHOW_EXAMPLE_SUCCESS_MESSAGE,
                "n_demonstrations": len(self.demonstrations),
            }
        self.n_failed_show += 1
        return {
            "ok": False,
            "shown_to_student": False,
            "error": "The provided output does not match the rule.",
            "teacher_output": clone_grid(pred),
            "gold_output": clone_grid(gold),
            "note": "This pair was not shown to the Student. You may correct it and try again.",
        }

    def show_transformed_input(self, input_grid: Any) -> Dict[str, Any]:
        if self.phase != "teach":
            return {
                "ok": False,
                "error": "show_transformed_input is only valid before the exam.",
            }
        if (self.max_demonstrations is not None
                and len(self.demonstrations) >= self.max_demonstrations):
            return {
                "ok": False,
                "error": (
                    f"All {self.max_demonstrations} demonstrations have been shown. "
                    "The teaching set is complete."
                ),
                "budget_spent": True,
            }
        try:
            inp = _parse_grid(input_grid)
        except ValueError:
            self.n_failed_show += 1
            return {"ok": False, "error": INVALID_INPUT_OR_RULE_MESSAGE}
        try:
            gold = self._gold(inp)
        except RuntimeError:
            self.n_failed_show += 1
            return {"ok": False, "error": INVALID_INPUT_OR_RULE_MESSAGE}
        self._append_demo(GridPair(inp, gold))
        self.n_show_transformed += 1
        return {
            "ok": True,
            "shown_to_student": True,
            "pair": {"input": clone_grid(inp), "output": clone_grid(gold)},
            "n_demonstrations": len(self.demonstrations),
        }

    def prepare_probe(self, input_grid: Any) -> Dict[str, Any]:
        if self.phase != "teach":
            return {"ok": False, "error": "query_student is only valid before the exam."}
        try:
            inp = _parse_grid(input_grid)
        except ValueError:
            return {"ok": False, "error": INVALID_INPUT_OR_RULE_MESSAGE}
        try:
            gold = self._gold(inp)
        except RuntimeError:
            return {"ok": False, "error": INVALID_INPUT_OR_RULE_MESSAGE}
        return {"ok": True, "input": clone_grid(inp), "gold": clone_grid(gold)}

    def record_probe(self, inp: Grid, student_output: Optional[Grid], gold: Grid) -> Dict[str, Any]:
        correct = student_output is not None and is_equal_grid(student_output, gold)
        self.probes.append(
            {
                "input": clone_grid(inp),
                "student_output": clone_grid(student_output) if student_output is not None else None,
                "gold_output": clone_grid(gold),
                "correct": correct,
            }
        )
        self.n_query_student += 1
        return {
            "ok": True,
            "student_output": clone_grid(student_output) if student_output is not None else None,
            "gold_output": clone_grid(gold),
            "correct": correct,
            "shown_to_student": False,
            "n_query_student": self.n_query_student,
            "note": (
                "The student did not receive the gold pair. "
                "Call show_example with the gold pair, or show_transformed_input "
                "with this input, to teach it."
            ),
        }

    def _draw_exam_pairs(self, n: int, exclude: List[Grid]) -> Optional[List[GridPair]]:
        pairs: List[GridPair] = []
        rng = self.trial.rng
        verifier = self._verifier()
        for _ in range(n):
            sampled = sample_consistent_dynamic_pair(
                self.trial.task,
                verifier,
                rng,
                exclude_inputs=exclude or None,
                max_tries=200,
            )
            if sampled is None:
                return None
            gold = self._gold(sampled.input)
            pairs.append(GridPair(clone_grid(sampled.input), gold))
            exclude.append(clone_grid(sampled.input))
        return pairs

    def predraw_exam(self) -> Dict[str, Any]:
        """Fix the exam items before teaching so the teacher can be checked on them."""
        if self.phase != "teach" or self.demonstrations or self.probes:
            return {"ok": False, "error": "predraw_exam must run before any teaching."}
        pairs = self._draw_exam_pairs(self.exam_n, self._seen_inputs())
        if pairs is None:
            return {"ok": False, "sampler_exhausted": True,
                    "message": f"Could not sample {self.exam_n} distinct exam pairs."}
        self.exam_pairs = pairs
        self.exam_predrawn = True
        return {"ok": True, "exam_n": len(pairs)}

    def record_teacher_exam(self, predictions: List[Optional[Grid]]) -> Dict[str, Any]:
        self.teacher_exam_predictions = [clone_grid(p) if p is not None else None for p in predictions]
        self.teacher_exam_correct = [
            p is not None and is_equal_grid(p, pair.output)
            for p, pair in zip(self.teacher_exam_predictions, self.exam_pairs)
        ]
        k = sum(1 for v in self.teacher_exam_correct if v)
        self.teacher_exam_passed = bool(self.exam_pairs) and k == len(self.exam_pairs)
        return {"ok": True, "n_correct": k, "exam_n": len(self.exam_pairs), "passed": self.teacher_exam_passed}

    def start_exam(self) -> Dict[str, Any]:
        if self.phase != "teach":
            return {"ok": False, "error": "start_exam is only valid during teaching."}
        exclude = self._seen_inputs()
        if self.exam_predrawn:
            # An item the teacher has since shown or probed is no longer held
            # out; swap it for a fresh draw rather than tell the teacher which
            # inputs the exam holds. The teacher check ran on the original.
            pairs = []
            for pair in self.exam_pairs:
                if any(is_equal_grid(pair.input, g) for g in exclude):
                    fresh = self._draw_exam_pairs(1, exclude)
                    if fresh is None:
                        return {"ok": False, "sampler_exhausted": True,
                                "message": "Could not replace a leaked exam item."}
                    pairs.extend(fresh)
                    self.exam_replaced += 1
                else:
                    pairs.append(pair)
                    exclude.append(clone_grid(pair.input))
        else:
            pairs = self._draw_exam_pairs(self.exam_n, exclude)
            if pairs is None:
                return {
                    "ok": False,
                    "sampler_exhausted": True,
                    "message": (
                        f"Could not sample {self.exam_n} distinct exam pairs "
                        f"({len(exclude)} prior input(s) excluded)."
                    ),
                }
        self.exam_pairs = pairs
        self.exam_predictions = [None] * len(pairs)
        self.exam_correct = [None] * len(pairs)
        self.exam_index = 0
        self.phase = "exam"
        first = pairs[0]
        return {
            "ok": True,
            "phase": "exam",
            "exam_n": self.exam_n,
            "n_demonstrations": len(self.demonstrations),
            "n_query_student": self.n_query_student,
            "message": (
                f"Exam started with {self.exam_n} held-out generator inputs. "
                "The student will answer them one at a time with no feedback."
            ),
            "first_test_input": clone_grid(first.input),
        }

    def current_exam_input(self) -> Optional[Grid]:
        if self.phase != "exam" or self.exam_index >= len(self.exam_pairs):
            return None
        return clone_grid(self.exam_pairs[self.exam_index].input)

    def submit_exam_answer(self, grid: Any) -> Dict[str, Any]:
        if self.phase != "exam":
            return {"ok": False, "error": "submit_prediction is only valid during the exam."}
        if self.exam_index >= len(self.exam_pairs):
            return {"ok": False, "error": "Exam already complete."}
        gold = self.exam_pairs[self.exam_index].output
        pred: Optional[Grid] = None
        try:
            pred = _parse_grid(grid)
            ok = is_equal_grid(pred, gold)
        except ValueError:
            ok = False
            pred = None
        self.exam_predictions[self.exam_index] = pred
        self.exam_correct[self.exam_index] = ok
        idx = self.exam_index
        self.exam_index += 1
        remaining = self.exam_n - self.exam_index
        if self.exam_index >= self.exam_n:
            self.phase = "done"
        return {
            "ok": True,
            "recorded": True,
            "exam_index": idx + 1,
            "exam_n": self.exam_n,
            "remaining": remaining,
            "done": self.phase == "done",
        }

    def mark_exam_unanswered(self) -> Dict[str, Any]:
        """Count a missing student submission as incorrect and advance."""
        if self.phase != "exam":
            return {"ok": False, "error": "Exam is not in progress."}
        if self.exam_index >= len(self.exam_pairs):
            return {"ok": False, "error": "Exam already complete."}
        idx = self.exam_index
        self.exam_predictions[idx] = None
        self.exam_correct[idx] = False
        self.exam_index += 1
        remaining = self.exam_n - self.exam_index
        if self.exam_index >= self.exam_n:
            self.phase = "done"
        return {
            "ok": True,
            "recorded": True,
            "exam_index": idx + 1,
            "exam_n": self.exam_n,
            "remaining": remaining,
            "done": self.phase == "done",
            "student_failed_to_submit": True,
        }

    def exam_score(self) -> Dict[str, Any]:
        n = len(self.exam_correct)
        k = sum(1 for v in self.exam_correct if v is True)
        return {
            "exam_correct": k,
            "exam_n": n,
            "exam_score": (k / n) if n else None,
        }


def create_inverse_query_session(
    *,
    seed: int,
    task_id: Optional[str] = None,
    dataset: str = "arc",
    exam_n: int = 10,
    include_teacher_sample: bool = True,
) -> InverseQuerySession:
    """Build a teacher/student trial (no hot-start leak to the student)."""
    if exam_n < 1:
        raise ValueError("exam_n must be >= 1")
    trial = create_trial_session(
        seed=seed,
        task_id=task_id,
        dataset=dataset,
        hot_start=False,
        noisy_science=False,
        re_trials=False,
        fixed_test=False,
    )
    # The gold oracle is the slot pick_verifier pinned -- the task's canonical
    # verifier. It used to be swapped for a more readable one here, which put
    # the exam in the hands of a verifier the census may have rejected.
    session = InverseQuerySession(
        trial=trial,
        programs=load_task_programs(trial),
        exam_n=exam_n,
        include_teacher_sample=include_teacher_sample,
    )
    if include_teacher_sample:
        sampled = sample_consistent_dynamic_pair(
            session.trial.task,
            session._verifier(),
            session.trial.rng,
            max_tries=200,
        )
        if sampled is not None:
            try:
                gold = session._gold(sampled.input)
            except RuntimeError:
                gold = None
            if gold is not None:
                session.teacher_sample = GridPair(clone_grid(sampled.input), clone_grid(gold))
    return session
