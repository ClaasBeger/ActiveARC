"""Guard against generator pairs that are provably ambiguous — per task, never globally.

Generators and verifiers sometimes disagree. Three causes, needing three answers:

* **the verifier is wrong** — fix the verifier;
* **the generator is wrong** — fix the generator;
* **the instance is ambiguous** — the rule genuinely does not determine an output,
  so no implementation can be right. Only this third case may be filtered.

Filtering by default would paper over the first two, which is exactly the bug class
this project cares about (a golf verifier returning well-formed garbage off its
training distribution looks identical to an ambiguous instance if you only check
"verifier disagrees"). So a task is filtered **only when it appears in
:data:`KNOWN_AMBIGUOUS`**, with the evidence recorded alongside it. Everything else
is audited and reported, never silently dropped.

Dependency-free (plain lists of lists) so it can be vendored into PotARCin
unchanged. Keep the two copies identical.
"""

from __future__ import annotations

import copy
import signal
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

Grid = List[List[int]]
Verifier = Callable[[Grid], Grid]

DEFAULT_TIMEOUT_S = 2.0

# Tasks whose generator can emit instances the rule does not determine. Each entry
# must record *why* — an ambiguity established by investigation, not a hunch.
KNOWN_AMBIGUOUS: Dict[str, str] = {
    "0e206a2e": (
        "ARC-GEN task018 clones each sprite under rotates=randint(1,4) and hides the "
        "common colour in the input, so the transform leaves no trace. When the three "
        "marker cells are symmetric (e.g. collinear on a diagonal, which the "
        "generator's 'not all in a line' guard does not exclude), two transforms map "
        "the key onto the same target but stamp different cells; a second sprite whose "
        "markers coincide under a transform does the same. Verified over 400 draws: "
        "16 of 17 disagreements have a target matched by >1 (template, transform) "
        "pair, and re_arc's output is always a strict superset of the generator's. "
        "The generator's choice is a uniform random draw and is unrecoverable."
    ),
    "50846271": (
        "ARC-GEN task_50846271 ('underneath2') draws crosses *underneath* random "
        "static: a cross cell landing on static becomes cyan and is then rendered "
        "as ordinary gray in the input, while a cell on empty space stays red. A "
        "cross with too little red left visible is not reconstructable, and one "
        "whose cells all land on static leaves no trace at all yet is still "
        "revealed in the output. The generator source carries the matching "
        "'# TODO: ensure center&length known' (still unfixed upstream as of "
        "2026-04-18; the file is byte-identical to our copy). Verified over 400 "
        "draws: 11 disagreements, 9 where the generator reveals cells the verifier "
        "cannot infer and 2 where centre/length are resolved differently, while the "
        "verifier is 4/4 on the original examples and 262/262 on the committed pool."
    ),
}


@contextmanager
def _time_limit(seconds: float) -> Iterator[None]:
    """Wall-clock cap for one verifier call (main thread only; no-op elsewhere)."""
    if seconds <= 0 or not hasattr(signal, "SIGALRM"):
        yield
        return

    def _raise(_signum: int, _frame: Any) -> None:
        raise TimeoutError(f"verifier call exceeded {seconds}s")

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


def _grids_equal(a: Optional[Grid], b: Optional[Grid]) -> bool:
    if a is None or b is None:
        return False
    if len(a) != len(b):
        return False
    return all(
        len(ra) == len(rb) and all(int(x) == int(y) for x, y in zip(ra, rb))
        for ra, rb in zip(a, b)
    )


def _as_pair(pair: Any) -> Tuple[Grid, Grid]:
    """Accept GridPair-like objects, dicts, or (input, output) tuples."""
    if hasattr(pair, "input") and hasattr(pair, "output"):
        return pair.input, pair.output
    if isinstance(pair, dict):
        return pair["input"], pair["output"]
    inp, out = pair
    return inp, out


def is_known_ambiguous(task_id: Optional[str], *, allow: Optional[Dict[str, str]] = None) -> bool:
    """True if *task_id* is on the ambiguity allowlist."""
    table = KNOWN_AMBIGUOUS if allow is None else allow
    return bool(task_id) and task_id in table


def verifier_reproduces(
    verifier: Verifier,
    inp: Grid,
    out: Grid,
    *,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> bool:
    """True if *verifier* maps *inp* to exactly *out* (errors and timeouts are False)."""
    try:
        with _time_limit(timeout_s):
            produced = verifier(copy.deepcopy(inp))
    except Exception:
        return False
    return _grids_equal(produced, out)


def filter_pairs(
    verifier: Optional[Verifier],
    pairs: Sequence[Any],
    *,
    task_id: Optional[str] = None,
    allow: Optional[Dict[str, str]] = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> Tuple[List[Any], List[Any]]:
    """Split *pairs* into ``(kept, dropped)`` — but only for allowlisted tasks.

    For any task not in :data:`KNOWN_AMBIGUOUS` (or *allow*), nothing is dropped:
    a disagreement there is a bug to investigate, not noise to remove. Use
    :func:`audit_pairs` to surface those.
    """
    if verifier is None or not is_known_ambiguous(task_id, allow=allow):
        return list(pairs), []
    kept: List[Any] = []
    dropped: List[Any] = []
    for pair in pairs:
        inp, out = _as_pair(pair)
        target = kept if verifier_reproduces(verifier, inp, out, timeout_s=timeout_s) else dropped
        target.append(pair)
    return kept, dropped


def audit_pairs(
    verifier: Verifier,
    pairs: Iterable[Any],
    *,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> dict:
    """Counts for a set of pairs: reproduced, mismatched, verifier errors.

    Mismatches are data problems (an invalid or ambiguous pair); errors are
    verifier robustness problems. Reporting them separately matters — conflating
    them hides which side is at fault.
    """
    n = ok = mismatch = error = 0
    for pair in pairs:
        n += 1
        inp, out = _as_pair(pair)
        try:
            with _time_limit(timeout_s):
                produced = verifier(copy.deepcopy(inp))
        except Exception:
            error += 1
            continue
        if _grids_equal(produced, out):
            ok += 1
        else:
            mismatch += 1
    return {"n": n, "reproduced": ok, "mismatched": mismatch, "verifier_error": error}
