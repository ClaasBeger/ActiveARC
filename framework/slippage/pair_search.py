"""Slippage pair search: narrow vs broad (RE-ARC) verifiers on ARC-AGI-1.

A **slippage pair** for a task is:

* **broad** — the ``re_arc`` verifier, which already passes the ARC-GEN
  distribution (train / test / ARC-GEN stable / ARC-GEN dynamic50), and
* **narrow** — another valid verifier slot (``google`` / ``keymoon`` /
  ``neurips`` / ``custom``) that also passes that ARC-GEN distribution, but
  **fails on a majority** of RE-ARC samples.

These pairs are candidates for on-the-fly adaptation experiments: a hypothesis
valid on the narrow (ARC-GEN-like) support may break under broader RE-ARC inputs.
"""

from __future__ import annotations

import copy
import json
import signal
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence

from framework.grids import GridPair, is_equal_grid
from framework.tasks.arc_dataset import ensure_verifier_slots, load_task
from framework.tasks.base import ArcTask, Verifier
from framework.verifier_selection import (
    VerifierSlot,
    _callable_for_slot,
    csv_slots_for_task,
    default_verifiers_csv_path,
    eligible_task_ids_from_csv,
)

NARROW_SLOTS: tuple[VerifierSlot, ...] = ("google", "keymoon", "neurips", "custom")
BROAD_SLOT: VerifierSlot = "re_arc"


class _PairTimeout(Exception):
    pass


@contextmanager
def _time_limit(seconds: float) -> Iterator[None]:
    """Best-effort wall-clock limit for a single verifier call (Unix signals)."""
    if seconds <= 0 or not hasattr(signal, "SIGALRM"):
        yield
        return

    def _handler(signum, frame):  # noqa: ANN001
        raise _PairTimeout()

    previous = signal.signal(signal.SIGALRM, _handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, previous)


@dataclass(frozen=True)
class SlippagePair:
    """One narrow/broad verifier pairing for a single ARC-AGI-1 task."""

    task_id: str
    broad_slot: VerifierSlot
    narrow_slot: VerifierSlot
    n_re_arc_scored: int
    broad_fail_count: int
    narrow_fail_count: int
    broad_fail_rate: float
    narrow_fail_rate: float
    csv_valid_slots: List[VerifierSlot]
    n_re_arc_available: int
    n_arc_gen_stable: int

    def to_dict(self) -> dict:
        return asdict(self)


def _score_fail_count(
    v: Verifier,
    pairs: Sequence[GridPair],
    *,
    pair_timeout_s: float = 0.5,
) -> int:
    fails = 0
    for p in pairs:
        try:
            with _time_limit(pair_timeout_s):
                out = v(copy.deepcopy(p.input))
            if not is_equal_grid(out, p.output):
                fails += 1
        except Exception:
            fails += 1
    return fails


def _select_re_arc_pairs(task: ArcTask, max_pairs: int) -> List[GridPair]:
    """Prefer committed RE-ARC stable pairs; fall back to dynamic generation."""
    pairs: List[GridPair] = []
    if task.re_arc_synthetic_pairs:
        pairs = list(task.re_arc_synthetic_pairs)
    elif task.re_arc_generator is not None:
        try:
            pairs = list(task.re_arc_generator(max(max_pairs, 1)))
        except Exception:
            pairs = []
    if max_pairs > 0 and len(pairs) > max_pairs:
        pairs = pairs[:max_pairs]
    return pairs


def candidate_task_ids(*, csv_path: Path | None = None) -> List[str]:
    """Tasks whose CSV lists ``re_arc`` plus at least one narrow slot."""
    path = csv_path if csv_path is not None else default_verifiers_csv_path()
    out: List[str] = []
    for tid in eligible_task_ids_from_csv(path):
        slots = set(csv_slots_for_task(tid, path))
        if BROAD_SLOT in slots and (slots & set(NARROW_SLOTS)):
            out.append(tid)
    return out


def find_slippage_pairs_for_task(
    task_id: str,
    *,
    max_re_arc_pairs: int = 200,
    majority_threshold: float = 0.5,
    max_broad_fail_rate: float = 0.1,
    pair_timeout_s: float = 0.5,
    csv_path: Path | None = None,
) -> List[SlippagePair]:
    """Return slippage pairs for one task (may be empty).

    Args:
      task_id: ARC-AGI-1 training task id.
      max_re_arc_pairs: Cap on RE-ARC pairs used for fail-rate scoring.
      majority_threshold: Narrow must fail strictly more than this fraction
          of RE-ARC pairs (default: majority = ``> 0.5``).
      max_broad_fail_rate: Broad (RE-ARC) verifier must fail at most this
          fraction of the scored RE-ARC pairs (sanity check).
      pair_timeout_s: Per-example verifier wall-clock timeout (counts as fail).
      csv_path: Optional override for ``task_valid_verifiers.csv``.
    """
    path = csv_path if csv_path is not None else default_verifiers_csv_path()
    slots = csv_slots_for_task(task_id, path)
    slot_set = set(slots)
    if BROAD_SLOT not in slot_set:
        return []
    narrow_candidates = [s for s in NARROW_SLOTS if s in slot_set]
    if not narrow_candidates:
        return []

    task = load_task(task_id, load_alternative_verifiers=False)
    ensure_verifier_slots(task, [BROAD_SLOT, *narrow_candidates])

    broad_fn = _callable_for_slot(task, BROAD_SLOT)
    if broad_fn is None:
        return []

    re_pairs = _select_re_arc_pairs(task, max_re_arc_pairs)
    if not re_pairs:
        return []

    broad_fails = _score_fail_count(
        broad_fn, re_pairs, pair_timeout_s=pair_timeout_s
    )
    broad_rate = broad_fails / len(re_pairs)
    if broad_rate > max_broad_fail_rate:
        return []

    n_stable = len(task.arc_gen_synthetic_pairs or [])
    n_re_avail = len(task.re_arc_synthetic_pairs or [])
    pairs_out: List[SlippagePair] = []
    for narrow_slot in narrow_candidates:
        narrow_fn = _callable_for_slot(task, narrow_slot)
        if narrow_fn is None:
            continue
        narrow_fails = _score_fail_count(
            narrow_fn, re_pairs, pair_timeout_s=pair_timeout_s
        )
        narrow_rate = narrow_fails / len(re_pairs)
        if narrow_rate <= majority_threshold:
            continue
        pairs_out.append(
            SlippagePair(
                task_id=task_id,
                broad_slot=BROAD_SLOT,
                narrow_slot=narrow_slot,
                n_re_arc_scored=len(re_pairs),
                broad_fail_count=broad_fails,
                narrow_fail_count=narrow_fails,
                broad_fail_rate=round(broad_rate, 6),
                narrow_fail_rate=round(narrow_rate, 6),
                csv_valid_slots=list(slots),
                n_re_arc_available=n_re_avail,
                n_arc_gen_stable=n_stable,
            )
        )
    return pairs_out


def find_slippage_pairs(
    task_ids: Optional[Iterable[str]] = None,
    *,
    max_re_arc_pairs: int = 200,
    majority_threshold: float = 0.5,
    max_broad_fail_rate: float = 0.1,
    pair_timeout_s: float = 0.5,
    csv_path: Path | None = None,
    progress: bool = True,
) -> List[SlippagePair]:
    """Scan ARC-AGI-1 tasks and collect all qualifying slippage pairs."""
    ids = list(task_ids) if task_ids is not None else candidate_task_ids(csv_path=csv_path)
    results: List[SlippagePair] = []
    for i, tid in enumerate(ids):
        if progress:
            print(
                f"[{i + 1}/{len(ids)}] {tid}  (pairs so far: {len(results)})",
                flush=True,
            )
        try:
            found = find_slippage_pairs_for_task(
                tid,
                max_re_arc_pairs=max_re_arc_pairs,
                majority_threshold=majority_threshold,
                max_broad_fail_rate=max_broad_fail_rate,
                pair_timeout_s=pair_timeout_s,
                csv_path=csv_path,
            )
        except Exception as exc:
            if progress:
                print(f"  skip {tid}: {type(exc).__name__}: {exc}", flush=True)
            continue
        results.extend(found)
    return results


def save_slippage_pairs(
    pairs: Sequence[SlippagePair],
    out_path: Path,
    *,
    meta: Optional[dict] = None,
) -> Path:
    """Write pairs (+ optional metadata) as JSON."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "meta": meta or {},
        "n_pairs": len(pairs),
        "n_tasks": len({p.task_id for p in pairs}),
        "pairs": [p.to_dict() for p in pairs],
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return out_path
