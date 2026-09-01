"""Slippage pair search: narrow vs broad (RE-ARC) on ARC-AGI-1.

A **slippage pair** for a task is:

* **broad** (``re_arc``) — covers the *narrow* example distribution: original
  train + test, plus ARC-GEN stable and dynamic samples (CSV-valid on that
  suite). This is the broad verifier/generator source used at test time.
* **narrow** (``google`` / ``keymoon`` / ``neurips`` / ``custom``) — also
  CSV-valid on that same narrow distribution (a previously valid hypothesis),
  but fails on a large fraction of RE-ARC samples (``>=`` majority threshold).

These pairs support on-the-fly adaptation experiments: a hypothesis that works
on ARC-GEN-like support may break under broader RE-ARC inputs.
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
    n_re_arc_stable_scored: int
    n_re_arc_dynamic_scored: int
    broad_fail_count: int
    narrow_fail_count: int
    broad_fail_rate: float
    narrow_fail_rate: float
    csv_valid_slots: List[VerifierSlot]
    n_re_arc_available: int
    n_arc_gen_stable: int

    def to_dict(self, *, is_canonical: bool | None = None) -> dict:
        out = asdict(self)
        if is_canonical is not None:
            out["is_canonical"] = is_canonical
        return out


def _canonical_narrow_slot_by_task(pairs: Sequence[SlippagePair]) -> dict[str, VerifierSlot]:
    """Pick the narrow slot with highest RE-ARC fail rate per task."""
    by_task: dict[str, list[SlippagePair]] = {}
    for p in pairs:
        by_task.setdefault(p.task_id, []).append(p)
    out: dict[str, VerifierSlot] = {}
    for tid, task_pairs in by_task.items():
        best = max(
            task_pairs,
            key=lambda p: (p.narrow_fail_rate, p.narrow_fail_count, p.narrow_slot),
        )
        out[tid] = best.narrow_slot
    return out


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


def _select_re_arc_pairs(
    task: ArcTask,
    *,
    max_stable_pairs: int,
    max_dynamic_pairs: int,
) -> tuple[List[GridPair], int, int]:
    """Stable RE-ARC zip pairs plus optional freshly generated dynamic pairs."""
    stable: List[GridPair] = list(task.re_arc_synthetic_pairs or [])
    if max_stable_pairs > 0 and len(stable) > max_stable_pairs:
        stable = stable[:max_stable_pairs]

    dynamic: List[GridPair] = []
    if max_dynamic_pairs > 0 and task.re_arc_generator is not None:
        try:
            dynamic = list(task.re_arc_generator(max_dynamic_pairs))
        except Exception:
            dynamic = []

    return stable + dynamic, len(stable), len(dynamic)


def candidate_task_ids(*, csv_path: Path | None = None) -> List[str]:
    """Tasks whose CSV lists ``re_arc`` plus at least one narrow slot.

    CSV validity means the slot passes train + test + ARC-GEN stable + dynamic50
    (the narrow example distribution).
    """
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
    max_re_arc_dynamic_pairs: int = 0,
    majority_threshold: float = 0.5,
    pair_timeout_s: float = 0.5,
    csv_path: Path | None = None,
) -> List[SlippagePair]:
    """Return slippage pairs for one task (may be empty).

    Args:
      task_id: ARC-AGI-1 training task id.
      max_re_arc_pairs: Cap on RE-ARC stable pairs used for fail-rate scoring.
      max_re_arc_dynamic_pairs: Fresh RE-ARC generator pairs to append (0 = none).
      majority_threshold: Narrow must fail at least this fraction of RE-ARC
          pairs (default ``>= 0.5``).
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

    re_pairs, n_stable_scored, n_dynamic_scored = _select_re_arc_pairs(
        task,
        max_stable_pairs=max_re_arc_pairs,
        max_dynamic_pairs=max_re_arc_dynamic_pairs,
    )
    if not re_pairs:
        return []

    # Informational only: broad is gated by CSV on the narrow distribution,
    # not by RE-ARC success.
    broad_fails = _score_fail_count(
        broad_fn, re_pairs, pair_timeout_s=pair_timeout_s
    )
    broad_rate = broad_fails / len(re_pairs)
    if broad_fails > 0:
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
        if narrow_rate < majority_threshold:
            continue
        pairs_out.append(
            SlippagePair(
                task_id=task_id,
                broad_slot=BROAD_SLOT,
                narrow_slot=narrow_slot,
                n_re_arc_scored=len(re_pairs),
                n_re_arc_stable_scored=n_stable_scored,
                n_re_arc_dynamic_scored=n_dynamic_scored,
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
    max_re_arc_dynamic_pairs: int = 0,
    majority_threshold: float = 0.5,
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
                max_re_arc_dynamic_pairs=max_re_arc_dynamic_pairs,
                majority_threshold=majority_threshold,
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
    canonical_by_task = _canonical_narrow_slot_by_task(pairs)
    payload_meta = dict(meta or {})
    payload_meta["canonical_narrow_rule"] = (
        "Per task, the narrow slot with highest narrow_fail_rate on scored RE-ARC "
        "samples; ties break on narrow_fail_count then narrow_slot."
    )
    payload_meta["canonical_narrow_by_task"] = canonical_by_task
    payload = {
        "meta": payload_meta,
        "n_pairs": len(pairs),
        "n_tasks": len({p.task_id for p in pairs}),
        "pairs": [
            p.to_dict(is_canonical=(p.narrow_slot == canonical_by_task[p.task_id]))
            for p in pairs
        ],
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return out_path
