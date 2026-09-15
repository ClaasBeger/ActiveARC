#!/usr/bin/env python3
"""Re-ask the oracle every question a recorded run asked, and flag what moved.

A trial is only meaningful if the answers the agent was given are the answers the
oracle would still give. Verifiers have since been rewritten and generators
fixed, so this replays each record against the current code::

    python -m pipelines.recheck_oracle_answers experiments/runs/arc_agi_1_astra_seed0 --write

Three things are checked per trial, all against the slot the trial actually used:

* the **hot-start pair** it was shown -- does the verifier still produce that
  output from that input;
* every **query** the agent submitted -- same question, recorded answer;
* the **final judgement** -- the verifier's answer for the test input against the
  grid the agent submitted, compared with the ``correct`` the record claims.

With ``--write`` each record gains an ``oracle_recheck`` block and stale trials
are marked ``"stale": true``; nothing else in the record is touched.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import signal
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

SKIP_FILES = {"manifest.json", "summary.json", "summary.jsonl", "program_scores.json",
              "oracle_recheck.json", "oracle_recheck_canon.json", "INVALID.json"}
# Read from the environment, not a module global set in main(): workers are
# spawned, so they re-import this module and would otherwise keep the default.
# Some golf verifiers need ~40s on a single 9x9 grid.
TIMEOUT_S = float(os.environ.get("RECHECK_TIMEOUT_S", "60"))


@contextmanager
def _limit(seconds: float):
    def _raise(*_a):
        raise TimeoutError("verifier timed out")

    old = signal.signal(signal.SIGALRM, _raise)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)



def _is_grid(value: Any) -> bool:
    """A real answer: a rectangle of colours, nothing else."""
    if not isinstance(value, list) or not value:
        return False
    for row in value:
        if not isinstance(row, list):
            return False
        for cell in row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                return False
    return True


def _load_task(dataset: str, task_id: str):
    if dataset == "parc":
        from framework.tasks.parc_dataset import load_parc_task

        return load_parc_task(task_id)
    if dataset == "conceptarc":
        from framework.integrations.conceptarc_adapter import load_conceptarc_task

        return load_conceptarc_task(task_id)
    from framework.tasks.arc_dataset import load_task

    return load_task(task_id, load_alternative_verifiers=True)


def _verifier(dataset: str, task, slot: Optional[str]):
    """The callable that answered this trial, as it behaves today."""
    if dataset in ("parc", "conceptarc"):
        return task.quinary_verifier or task.verifier
    from framework.verifier_selection import _callable_for_slot

    if slot:
        fn = _callable_for_slot(task, slot)
        if fn is not None:
            return fn
    from framework.active_arc.verifier_selection import list_valid_verifiers

    valid = list_valid_verifiers(task)
    return valid[0][1] if valid else task.verifier


def _answer(fn, grid):
    """What the verifier says now, plus why it could not say it."""
    try:
        with _limit(TIMEOUT_S):
            return fn(copy.deepcopy(grid)), None
    except TimeoutError:
        return None, "timeout"
    except Exception as exc:
        return None, type(exc).__name__


def _submitted_grid(record: Dict[str, Any]) -> Optional[List[List[int]]]:
    """The grid the trial was judged on: the last *accepted* submit_final_answer.

    A first submission can be rejected by the tool (a ragged grid, say) and
    corrected on the next turn; the verdict belongs to the corrected one. The
    first-call version of this once flagged such a trial as "verdict changed".
    Falls back to the last call when no result was recorded alongside.
    """
    accepted: Optional[List[List[int]]] = None
    last: Optional[List[List[int]]] = None
    for turn in record.get("transcript") or []:
        calls = turn.get("tool_calls") or []
        results = turn.get("tool_results") or []
        for i, call in enumerate(calls):
            if call.get("name") != "submit_final_answer":
                continue
            args = call.get("arguments")
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:
                    continue
            if not (isinstance(args, dict) and isinstance(args.get("grid"), list)):
                continue
            last = args["grid"]
            res = (results[i].get("result") or {}) if i < len(results) and isinstance(results[i], dict) else {}
            if res.get("ok") and res.get("done"):
                accepted = args["grid"]
    return accepted if accepted is not None else last


def recheck_record(path: Path) -> Dict[str, Any]:
    from framework.grids import is_equal_grid

    record = json.loads(path.read_text(encoding="utf-8"))
    task_id = record.get("task_id")
    dataset = record.get("dataset", "arc")
    trial = record.get("trial") or {}
    slot = trial.get("verifier_slot")
    out: Dict[str, Any] = {
        "task_id": task_id, "dataset": dataset, "slot": slot, "path": str(path),
    }
    # --canon: judge the recorded answers by the task's canonical verifier rather
    # than the slot the trial happened to pin. A slot the census rejects may
    # still have answered every question this trial asked correctly; this is
    # how that is decided.
    if os.environ.get("RECHECK_CANON") == "1":
        canon = None
        if dataset == "arc":
            from framework.verifier_selection import csv_selected_slot_for_task
            canon = csv_selected_slot_for_task(task_id)
        elif dataset == "arc2":
            canon = "custom"        # canon.json orders the canonical candidate first
        if canon:
            out["canon_slot"] = canon
            slot = canon
    try:
        task = _load_task(dataset, task_id)
        fn = _verifier(dataset, task, slot)
    except Exception as exc:  # a task that no longer loads is itself a finding
        out.update(error=str(exc)[:120], stale=True)
        return out
    if fn is None:
        out.update(error="no verifier", stale=True)
        return out

    # 1. the example the trial opened with
    hot = trial.get("hot_start_pair") or {}
    if hot.get("input") is not None:
        got, why = _answer(fn, hot["input"])
        out["hot_start_ok"] = got is not None and is_equal_grid(got, hot.get("output"))
        if why:
            out["hot_start_why"] = why

    # 2. every question the agent asked
    queries = trial.get("query_history") or []
    moved: List[Dict[str, Any]] = []
    malformed: List[int] = []
    for i, q in enumerate(queries):
        if q.get("input") is None:
            continue
        if not _is_grid(q.get("output")):
            # The oracle handed the agent something that is not a grid at all --
            # a cell of None, or a value outside 0-9. Nothing can "still" match
            # it, and the trial was already running on a bad answer.
            malformed.append(i)
            continue
        got, why = _answer(fn, q["input"])
        if got is None or not is_equal_grid(got, q.get("output")):
            moved.append({"index": i, "raised": got is None, "why": why})
    out["queries"] = len(queries)
    out["queries_moved"] = moved
    out["queries_malformed"] = malformed

    # An ARC-AGI-2 task often ships several vendored verifiers. They agree on the
    # official examples and on generator draws, so nothing distinguishes them --
    # but they can still answer a novel query differently, and which one is first
    # depends on the environment (numpy decides whether some of them import at
    # all). An answer that another candidate still reproduces means the oracle
    # changed hands, not that the recorded answer was wrong.
    if moved and dataset == "arc2":
        try:
            from framework.integrations.agi2_verifiers import get_agi2_valid_verifiers

            others = [f for _cid, f in get_agi2_valid_verifiers(task_id) if f is not fn]
        except Exception:
            others = []
        reproduced = 0
        for m in moved:
            q = queries[m["index"]]
            if any(is_equal_grid(a, q.get("output"))
                   for a in (_answer(o, q["input"])[0] for o in others) if a is not None):
                m["reproduced_by_other_candidate"] = True
                reproduced += 1
        out["moved_by_candidate_switch"] = reproduced

    # 3. the verdict the trial recorded
    test_input = trial.get("test_input")
    submitted = _submitted_grid(record)
    if test_input is not None and submitted is not None:
        expected, _why = _answer(fn, test_input)
        now_correct = expected is not None and is_equal_grid(expected, submitted)
        was_correct = bool(record.get("correct"))
        out["correct_recorded"] = was_correct
        out["correct_now"] = now_correct
        out["verdict_moved"] = now_correct != was_correct
    # A verifier that timed out has not changed its mind; keep that apart from a
    # real disagreement so a slow oracle cannot masquerade as a stale record.
    unexplained = [m for m in moved
                   if not m.get("reproduced_by_other_candidate")
                   and m.get("why") != "timeout"]
    out["queries_timed_out"] = sum(1 for m in moved if m.get("why") == "timeout")
    out["stale"] = bool(
        out.get("hot_start_ok") is False or unexplained or malformed
        or out.get("verdict_moved")
    )
    if moved and not unexplained:
        out["note"] = "answers moved to another vendored candidate, none contradicted"
    return out


def _worker(path_str: str) -> Dict[str, Any]:
    return recheck_record(Path(path_str))


def main() -> None:
    p = argparse.ArgumentParser(description="Recheck recorded oracle answers")
    p.add_argument("run_dirs", nargs="+", type=str)
    p.add_argument("--jobs", type=int, default=8)
    p.add_argument("--timeout", type=float, default=60.0,
                   help="Seconds a single verifier call may take (default 60).")
    p.add_argument("--write", action=argparse.BooleanOptionalAction, default=False,
                   help="Annotate each trial JSON with an oracle_recheck block.")
    p.add_argument("--canon", action="store_true",
                   help="Replay against each task's canonical verifier instead of the pinned slot.")
    args = p.parse_args()
    os.environ["RECHECK_TIMEOUT_S"] = str(args.timeout)
    os.environ["RECHECK_CANON"] = "1" if args.canon else "0"

    import multiprocessing as mp

    for run_dir in args.run_dirs:
        d = Path(run_dir)
        files = sorted(f for f in d.glob("*.json") if f.name not in SKIP_FILES)
        if not files:
            print("%-36s (no trial files)" % d.name)
            continue
        results: List[Dict[str, Any]] = []
        # spawn, not fork: the vendored ARC-AGI-2 verifiers import numpy, which
        # fails in a process forked from one that already loaded it.
        with mp.get_context("spawn").Pool(args.jobs) as pool:
            for r in pool.imap_unordered(_worker, [str(f) for f in files]):
                results.append(r)
        stale = [r for r in results if r.get("stale")]
        moved_q = sum(len(r.get("queries_moved") or []) for r in results)
        malformed_q = sum(len(r.get("queries_malformed") or []) for r in results)
        timed = sum(r.get("queries_timed_out") or 0 for r in results)
        verdicts = [r for r in results if r.get("verdict_moved")]
        hot = [r for r in results if r.get("hot_start_ok") is False]
        print("%-36s %3d trials | stale %3d | hot-start moved %3d | queries moved %3d "
              "(timeouts %d) | malformed answers %d | verdicts changed %3d" % (
                  d.name, len(results), len(stale), len(hot), moved_q, timed,
                  malformed_q, len(verdicts)))
        for r in sorted(stale, key=lambda r: r["task_id"]):
            print("    %-12s slot=%-8s hot=%s queries_moved=%d verdict %s->%s" % (
                r["task_id"], r.get("slot"), r.get("hot_start_ok"),
                len(r.get("queries_moved") or []),
                r.get("correct_recorded"), r.get("correct_now")))
        if args.write:
            stamp = datetime.now(timezone.utc).isoformat()
            by_path = {r["path"]: r for r in results}
            for f in files:
                r = by_path.get(str(f))
                if r is None:
                    continue
                rec = json.loads(f.read_text(encoding="utf-8"))
                # A canon replay is a different question from the pinned-slot one,
                # so it lives under its own key rather than overwriting the first.
                key = "oracle_recheck_canon" if args.canon else "oracle_recheck"
                rec[key] = {k: v for k, v in r.items() if k != "path"}
                rec[key]["checked_at"] = stamp
                f.write_text(json.dumps(rec, indent=2), encoding="utf-8")
            summary = {
                "run": d.name, "checked_at": stamp, "trials": len(results),
                "stale": len(stale), "hot_start_moved": len(hot),
                "queries_moved": moved_q, "verdicts_changed": len(verdicts),
                "stale_tasks": sorted(r["task_id"] for r in stale),
            }
            (d / ("oracle_recheck_canon.json" if args.canon else "oracle_recheck.json")).write_text(json.dumps(summary, indent=2),
                                                   encoding="utf-8")


if __name__ == "__main__":
    main()
