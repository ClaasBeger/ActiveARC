"""Score a model-submitted Python program against the standard ARC suites.

The program stage replaces the single test grid with a rule implementation, which
is then run on the four sets used to validate verifiers:

``train``              original ARC training pairs
``test``               original ARC test pairs
``generator_stable``   committed ARC-GEN pairs (``arc_gen_synthetic_pairs``)
``generator_dynamic``  fresh draws from ``arc_gen_generator`` (50 by default)

A program counts as correct only if it reproduces every pair in every available
set, matching how :func:`verifier_matches_train_test_stable_dynamic50` gates a
verifier.
"""

from __future__ import annotations

import copy
import random
import time
import signal
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterator, List, Optional, Sequence, Tuple

from framework.grids import Grid, GridPair, is_equal_grid, validate_grid
from framework.tasks.base import ArcTask

EVAL_SET_NAMES: Tuple[str, ...] = ("train", "test", "generator_stable", "generator_dynamic")

# Entry points tried in order; the first callable found wins.
ENTRY_POINT_NAMES: Tuple[str, ...] = ("transform", "solve", "transform_grid", "main", "p")

# Official pairs that contradict their own task's rule, so no correct program can
# reproduce them. Each entry must say why; this is not a place to hide failures.
OFFICIAL_PAIR_EXCEPTIONS: Dict[str, Dict[str, Tuple[int, ...]]] = {
    "e5062a87": {
        "train": (1,),
        # The rule is "stamp the shape wherever it fits on the black cells".
        # train[1] leaves one such placement unmarked -- it fits at (1,3) and at
        # (5,6), the two do not overlap or interact, and nothing in the picture
        # separates them. The vendored verifiers only match it by way of a
        # hash()-keyed special case, which then misfires on unrelated grids.
    },
}

DEFAULT_DYNAMIC_N = 50
DEFAULT_CALL_TIMEOUT_S = 2.0
# Caps on the fresh draw: a per-draw alarm and an overall budget per task.
DEFAULT_DRAW_TIMEOUT_S = 5.0
# Generous: the full 50 is wanted wherever the generator can supply it, so the
# budget only exists to stop a task that never will.
DEFAULT_DYNAMIC_BUDGET_S = 600.0
DEFAULT_DRAW_GIVE_UP = 60


class ProgramError(Exception):
    """Program could not be loaded (syntax error, no entry point, ...)."""


@contextmanager
def _time_limit(seconds: float) -> Iterator[None]:
    """SIGALRM-based wall-clock cap (main thread only; no-op if unavailable)."""
    if seconds <= 0 or not hasattr(signal, "SIGALRM"):
        yield
        return

    def _raise(_signum: int, _frame: Any) -> None:
        raise TimeoutError(f"program call exceeded {seconds}s")

    try:
        previous = signal.signal(signal.SIGALRM, _raise)
    except ValueError:  # not the main thread
        yield
        return
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, previous)


def load_program(code: str) -> Callable[[Grid], Grid]:
    """Execute *code* and return its entry-point callable.

    Raises :class:`ProgramError` if it does not compile or exposes no usable function.
    """
    if not isinstance(code, str) or not code.strip():
        raise ProgramError("empty program")
    namespace: Dict[str, Any] = {}
    try:
        compiled = compile(code, "<submitted_program>", "exec")
    except SyntaxError as e:
        raise ProgramError(f"SyntaxError: {e}") from e
    try:
        with _time_limit(DEFAULT_CALL_TIMEOUT_S):
            exec(compiled, namespace)  # noqa: S102 - research harness, user's own machine
    except Exception as e:
        raise ProgramError(f"{type(e).__name__} at import time: {e}") from e

    for name in ENTRY_POINT_NAMES:
        fn = namespace.get(name)
        if callable(fn):
            return fn
    defined = [
        v
        for k, v in namespace.items()
        if callable(v) and not k.startswith("_") and getattr(v, "__module__", None) is None
    ]
    if len(defined) == 1:
        return defined[0]
    raise ProgramError(
        "no entry point found; define a function named "
        + " or ".join(ENTRY_POINT_NAMES[:2])
        + " that takes one grid and returns a grid"
    )


@dataclass
class SetResult:
    """Per-set outcome for one submitted program."""

    n: int = 0
    n_correct: int = 0
    n_error: int = 0
    first_error: Optional[str] = None

    @property
    def all_correct(self) -> bool:
        return self.n > 0 and self.n_correct == self.n

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n": self.n,
            "n_correct": self.n_correct,
            "n_error": self.n_error,
            "first_error": self.first_error,
            "all_correct": self.all_correct,
        }


@dataclass
class ProgramEvalResult:
    """Aggregate outcome across the evaluation sets."""

    loaded: bool
    error: Optional[str] = None
    sets: Dict[str, SetResult] = field(default_factory=dict)
    # Generator/verifier disagreement on a task that is NOT allowlisted as
    # ambiguous: surfaced rather than filtered, because it indicates a bug.
    audit: Optional[Dict[str, int]] = None

    @property
    def n_total(self) -> int:
        return sum(s.n for s in self.sets.values())

    @property
    def n_correct(self) -> int:
        return sum(s.n_correct for s in self.sets.values())

    @property
    def all_correct(self) -> bool:
        """Every pair in every evaluated set reproduced (at least one set present)."""
        if not self.loaded or not self.sets:
            return False
        return all(s.all_correct for s in self.sets.values() if s.n > 0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loaded": self.loaded,
            "error": self.error,
            "all_correct": self.all_correct,
            "n_total": self.n_total,
            "n_correct": self.n_correct,
            "accuracy": round(self.n_correct / self.n_total, 6) if self.n_total else 0.0,
            "sets": {name: s.to_dict() for name, s in self.sets.items()},
            "unfiltered_disagreements": self.audit,
        }


def _dynamic_pairs(
    task: ArcTask,
    n: int,
    rng: random.Random,
    *,
    budget_s: float = DEFAULT_DYNAMIC_BUDGET_S,
) -> List[GridPair]:
    """Up to *n* fresh pairs, drawn one at a time under a wall-clock budget.

    Asking a generator for all *n* at once means one pathological draw can hang
    the whole run -- a few generators rejection-sample and occasionally spin for
    minutes. Drawing singly with a cap keeps whatever arrived in time.
    """
    gen = task.arc_gen_generator
    if gen is None:
        return []
    pairs: List[GridPair] = []
    deadline = time.monotonic() + budget_s if budget_s > 0 else None
    misses = 0
    while len(pairs) < n:
        if deadline is not None and time.monotonic() > deadline:
            break
        if misses >= DEFAULT_DRAW_GIVE_UP:
            break  # the generator is not going to produce any more
        try:
            with _time_limit(DEFAULT_DRAW_TIMEOUT_S):
                try:
                    drawn = list(gen(1, rng))
                except TypeError:
                    drawn = list(gen(1))
        except Exception:
            # One draw spinning says nothing about the next: some generators
            # rejection-sample and hang occasionally. Keep asking.
            misses += 1
            continue
        if not drawn:
            misses += 1
            continue
        misses = 0
        pairs.extend(drawn)
    return pairs[:n]


def evaluation_sets(
    task: ArcTask,
    *,
    rng: Optional[random.Random] = None,
    dynamic_n: int = DEFAULT_DYNAMIC_N,
    guard_verifier: Optional[Callable[[Grid], Grid]] = None,
    stable_pairs: Optional[Sequence[GridPair]] = None,
    skip_dynamic: bool = False,
) -> Dict[str, List[GridPair]]:
    """The four standard suites for *task* (absent sources yield empty lists).

    With *guard_verifier*, pairs the verifier does not reproduce are dropped (see
    ``framework.tasks.pair_guard``): generators can emit instances the rule does
    not determine, and scoring a program against those punishes correct answers.
    """
    rng = rng or random.Random(0)
    test_pairs: List[GridPair] = []
    for i in range(min(len(task.test_inputs or []), len(task.test_outputs or []))):
        test_pairs.append(GridPair(task.test_inputs[i], task.test_outputs[i]))
    sets = {
        "train": list(task.train_pairs or []),
        "test": test_pairs,
        # P-ARC keeps its committed pool in p_arc_stable_pairs, not arc_gen_synthetic_pairs.
        # A frozen set built for this task is the evaluation suite when there is
        # one; the committed pool is the fallback.
        "generator_stable": list(
            stable_pairs
            if stable_pairs is not None
            else (task.arc_gen_synthetic_pairs or task.p_arc_stable_pairs or [])
        ),
        # A generator with only a handful of distinct pairs cannot supply a fresh
        # sample: drawing from it would re-test the frozen set under another name.
        "generator_dynamic": [] if skip_dynamic else _dynamic_pairs(task, dynamic_n, rng),
    }
    for split, indices in (OFFICIAL_PAIR_EXCEPTIONS.get(task.task_id) or {}).items():
        sets[split] = [p for i, p in enumerate(sets.get(split) or [])
                       if i not in set(indices)]
    if guard_verifier is not None:
        from framework.tasks.pair_guard import audit_pairs, filter_pairs, is_known_ambiguous

        if is_known_ambiguous(task.task_id):
            for name, pairs in sets.items():
                kept, _dropped = filter_pairs(
                    guard_verifier, pairs, task_id=task.task_id
                )
                sets[name] = kept
        else:
            # Not an allowlisted ambiguity: leave the pairs in place. A
            # disagreement here means the verifier or the generator is wrong, and
            # silently dropping it would hide exactly that.
            report = audit_pairs(guard_verifier, sets["generator_dynamic"])
            if report["mismatched"] or report["verifier_error"]:
                sets.setdefault("_audit", [])  # type: ignore[arg-type]
                sets["_audit"] = report  # type: ignore[assignment]
    return sets


def _score_set(
    fn: Callable[[Grid], Grid],
    pairs: Sequence[GridPair],
    *,
    call_timeout_s: float,
) -> SetResult:
    result = SetResult(n=len(pairs))
    for pair in pairs:
        try:
            with _time_limit(call_timeout_s):
                out = fn(copy.deepcopy(pair.input))
            validate_grid(out)
        except Exception as e:  # timeout, crash, or malformed output
            result.n_error += 1
            if result.first_error is None:
                result.first_error = f"{type(e).__name__}: {e}"[:200]
            continue
        if is_equal_grid(out, pair.output):
            result.n_correct += 1
    return result


def evaluate_program(
    task: ArcTask,
    code: str,
    *,
    rng: Optional[random.Random] = None,
    dynamic_n: int = DEFAULT_DYNAMIC_N,
    call_timeout_s: float = DEFAULT_CALL_TIMEOUT_S,
    guard_verifier: Optional[Callable[[Grid], Grid]] = None,
    stable_pairs: Optional[Sequence[GridPair]] = None,
    skip_dynamic: bool = False,
) -> ProgramEvalResult:
    """Run *code* against train / test / generator-stable / generator-dynamic.

    Pass *guard_verifier* (the task's oracle) to drop pairs it cannot reproduce.
    """
    try:
        fn = load_program(code)
    except ProgramError as e:
        return ProgramEvalResult(loaded=False, error=str(e))

    sets = evaluation_sets(
        task,
        rng=rng,
        dynamic_n=dynamic_n,
        guard_verifier=guard_verifier,
        stable_pairs=stable_pairs,
        skip_dynamic=skip_dynamic,
    )
    audit = sets.pop("_audit", None)
    out = ProgramEvalResult(loaded=True)
    out.audit = audit  # type: ignore[attr-defined]
    for name in EVAL_SET_NAMES:
        pairs = sets.get(name) or []
        out.sets[name] = _score_set(fn, pairs, call_timeout_s=call_timeout_s)
    return out
