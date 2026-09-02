"""CT Pang pickle → ARC-AGI-2 training-task monotonic alignment."""

from __future__ import annotations

import json
import logging
import pickle
import signal
import sys
import types
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from pydantic import BaseModel

from .grid_utils import load_official_pairs, passes_official
from .paths import ARC_ORIGINAL, CTPANG_PICKLE, LOGS

logger = logging.getLogger(__name__)

_ALIGN_CASE_TIMEOUT_S = 2.0


class _AlignTimeout(Exception):
    pass


def _align_alarm_handler(signum, frame):  # noqa: ARG001
    raise _AlignTimeout()


class _Primitive(BaseModel):
    id: str
    python_code_str: str


class _Library(BaseModel):
    primitives: list[_Primitive]


def load_ct_pang_primitives(pickle_path: Path = CTPANG_PICKLE) -> List[_Primitive]:
    """Load ``saved_library_1000.pkl`` without importing epang's full ``src`` package."""
    pkg = types.ModuleType("src")
    models = types.ModuleType("src.models")
    models.Primitive = _Primitive  # type: ignore[attr-defined]
    models.Library = _Library  # type: ignore[attr-defined]
    sys.modules["src"] = pkg
    sys.modules["src.models"] = models
    with open(pickle_path, "rb") as f:
        lib = pickle.load(f)
    return list(lib.primitives)


def compile_transform(python_code_str: str) -> Callable:
    ns: Dict[str, Any] = {}
    # Many CT Pang programs use numpy.
    try:
        import numpy as np

        ns["np"] = np
        ns["numpy"] = np
    except ImportError:
        pass
    exec(python_code_str, ns, ns)
    fn = ns.get("transform")
    if not callable(fn):
        raise ValueError("pickle program has no callable transform()")
    return fn


@dataclass
class AlignmentDecision:
    program_index: int
    program_id: str
    task_id: Optional[str]
    status: str  # mapped | rejected_no_match | rejected_ambiguous | skipped
    window_searched: int
    candidate_task_ids: List[str] = field(default_factory=list)
    detail: str = ""


def _task_ids_lex_sorted_agi2_training() -> List[str]:
    """Lexicographically sorted ARC-AGI-2 training task IDs present as originals."""
    # Prefer full AGI-2 training listing if the clone exists; else all originals.
    agi2 = Path("/tmp/ARC-AGI-2/data/training")
    if agi2.is_dir():
        ids = sorted(p.stem for p in agi2.glob("*.json"))
        if len(ids) >= 1000:
            return ids
    # Fallback: every JSON in arc_original_train (includes AGI-1+AGI-2).
    return sorted(p.stem for p in ARC_ORIGINAL.glob("*.json"))


def _load_pairs_cache(task_ids: Sequence[str]) -> Dict[str, list]:
    cache: Dict[str, list] = {}
    missing = []
    for tid in task_ids:
        path = ARC_ORIGINAL / f"{tid}.json"
        if not path.is_file():
            missing.append(tid)
            continue
        data = json.loads(path.read_text())
        cache[tid] = load_official_pairs(data)
    if missing:
        logger.warning("Missing %d official JSONs for alignment (e.g. %s)", len(missing), missing[:5])
    return cache


def _passes(fn: Callable, pairs: list, *, timeout_s: float = _ALIGN_CASE_TIMEOUT_S) -> bool:
    """True if *fn* matches all official pairs within *timeout_s* wall time."""
    if timeout_s > 0 and hasattr(signal, "SIGALRM"):
        old = signal.signal(signal.SIGALRM, _align_alarm_handler)
        try:
            signal.setitimer(signal.ITIMER_REAL, timeout_s)
            try:
                ok, _ = passes_official(fn, pairs)
                return ok
            except _AlignTimeout:
                return False
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old)
    ok, _ = passes_official(fn, pairs)
    return ok


def _unique_perfect_matching(
    prog_indices: Sequence[int],
    task_indices: Sequence[int],
    edge: Callable[[int, int], bool],
) -> Optional[Dict[int, int]]:
    """If there is exactly one perfect matching covering all programs, return it.

    Programs may be fewer than tasks; every program must be matched to a distinct task.
    Uses exhaustive search (windows are small).
    """
    n = len(prog_indices)
    if n == 0:
        return {}
    if n > len(task_indices):
        return None

    solutions: List[Dict[int, int]] = []

    def rec(k: int, used: set, partial: Dict[int, int]) -> None:
        if len(solutions) > 1:
            return
        if k == n:
            solutions.append(dict(partial))
            return
        pi = prog_indices[k]
        for tj in task_indices:
            if tj in used:
                continue
            if not edge(pi, tj):
                continue
            used.add(tj)
            partial[pi] = tj
            rec(k + 1, used, partial)
            del partial[pi]
            used.remove(tj)

    rec(0, set(), {})
    if len(solutions) == 1:
        return solutions[0]
    return None


def align_ct_pang(
    *,
    initial_window: int = 8,
    max_window: int = 64,
    look_ahead_programs: int = 6,
) -> Tuple[Dict[int, str], List[AlignmentDecision]]:
    """Monotonic anchor alignment of pickle programs to lex-sorted AGI-2 training IDs.

    Never maps by order alone — every accepted edge must pass all official pairs.
    Ambiguous programs are left unmapped.
    """
    primitives = load_ct_pang_primitives()
    task_ids = _task_ids_lex_sorted_agi2_training()
    pairs_cache = _load_pairs_cache(task_ids)
    logger.info(
        "CT Pang align: %d programs × %d tasks (initial_window=%d max_window=%d)",
        len(primitives),
        len(task_ids),
        initial_window,
        max_window,
    )

    # Precompile programs
    compiled: List[Optional[Callable]] = []
    for p in primitives:
        try:
            compiled.append(compile_transform(p.python_code_str))
        except Exception as e:
            logger.warning("Program %s failed to compile: %s", p.id, e)
            compiled.append(None)

    pass_cache: Dict[Tuple[int, int], bool] = {}

    def edge(pi: int, tj: int) -> bool:
        key = (pi, tj)
        if key in pass_cache:
            return pass_cache[key]
        fn = compiled[pi]
        tid = task_ids[tj]
        if fn is None or tid not in pairs_cache:
            pass_cache[key] = False
            return False
        ok = _passes(fn, pairs_cache[tid])
        pass_cache[key] = ok
        return ok

    mappings: Dict[int, str] = {}
    decisions: List[AlignmentDecision] = []
    task_cursor = 0
    i = 0
    n_prog = len(primitives)

    while i < n_prog:
        if i % 25 == 0:
            logger.info(
                "CT Pang progress program=%d/%d mapped=%d cursor_task=%d cache=%d",
                i,
                n_prog,
                len(mappings),
                task_cursor,
                len(pass_cache),
            )
        if compiled[i] is None:
            decisions.append(
                AlignmentDecision(
                    program_index=i,
                    program_id=primitives[i].id,
                    task_id=None,
                    status="rejected_no_match",
                    window_searched=0,
                    detail="compile_failed",
                )
            )
            i += 1
            continue

        window = initial_window
        matches: List[int] = []
        while True:
            end = min(len(task_ids), task_cursor + window)
            matches = [j for j in range(task_cursor, end) if edge(i, j)]
            if matches or window >= max_window or end >= len(task_ids):
                break
            window = min(max_window, window * 2)

        if len(matches) == 1:
            j = matches[0]
            tid = task_ids[j]
            mappings[i] = tid
            decisions.append(
                AlignmentDecision(
                    program_index=i,
                    program_id=primitives[i].id,
                    task_id=tid,
                    status="mapped",
                    window_searched=window,
                    candidate_task_ids=[tid],
                    detail="unique_anchor",
                )
            )
            task_cursor = j + 1
            i += 1
            continue

        if len(matches) == 0:
            decisions.append(
                AlignmentDecision(
                    program_index=i,
                    program_id=primitives[i].id,
                    task_id=None,
                    status="rejected_no_match",
                    window_searched=window,
                    candidate_task_ids=[],
                    detail="no_official_pass_in_forward_window",
                )
            )
            i += 1
            continue

        # Ambiguous: try local monotonic perfect matching with a short look-ahead.
        end = min(len(task_ids), task_cursor + max(window, len(matches) + look_ahead_programs))
        batch_end = min(n_prog, i + look_ahead_programs)
        prog_batch = list(range(i, batch_end))
        task_batch = list(range(task_cursor, end))
        # Restrict to programs that have ≥1 edge in the batch window.
        usable_progs = [pi for pi in prog_batch if any(edge(pi, tj) for tj in task_batch)]
        matching = _unique_perfect_matching(usable_progs, task_batch, edge) if usable_progs else None

        if matching is not None and i in matching and len(matching) == len(usable_progs):
            # Accept only if the matching is contiguous from i for the first k programs
            # that participate; require program i mapped.
            ordered = sorted(matching.items(), key=lambda kv: kv[1])
            # Verify monotonic program index order matches task order
            prog_order = [pi for pi, _ in sorted(matching.items())]
            task_order = [matching[pi] for pi in prog_order]
            if prog_order == sorted(prog_order) and task_order == sorted(task_order):
                for pi, tj in sorted(matching.items()):
                    tid = task_ids[tj]
                    mappings[pi] = tid
                    decisions.append(
                        AlignmentDecision(
                            program_index=pi,
                            program_id=primitives[pi].id,
                            task_id=tid,
                            status="mapped",
                            window_searched=window,
                            candidate_task_ids=[task_ids[m] for m in matches] if pi == i else [],
                            detail="local_unique_perfect_matching",
                        )
                    )
                task_cursor = max(matching.values()) + 1
                i = max(matching.keys()) + 1
                continue

        decisions.append(
            AlignmentDecision(
                program_index=i,
                program_id=primitives[i].id,
                task_id=None,
                status="rejected_ambiguous",
                window_searched=window,
                candidate_task_ids=[task_ids[j] for j in matches],
                detail=f"ambiguous_matches={len(matches)}; no unique local perfect matching",
            )
        )
        i += 1

    LOGS.mkdir(parents=True, exist_ok=True)
    out_path = LOGS / "ct_pang_alignment.json"
    payload = {
        "n_programs": len(primitives),
        "n_tasks": len(task_ids),
        "n_mapped": len(mappings),
        "mappings": {str(k): v for k, v in sorted(mappings.items())},
        "decisions": [asdict(d) for d in decisions],
    }
    out_path.write_text(json.dumps(payload, indent=2))
    logger.info(
        "CT Pang alignment done: mapped=%d rejected=%d -> %s",
        len(mappings),
        sum(1 for d in decisions if d.status.startswith("rejected")),
        out_path,
    )
    return mappings, decisions
