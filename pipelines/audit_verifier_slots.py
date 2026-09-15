#!/usr/bin/env python3
"""Check every verifier a task could be given, not just the one it usually gets.

``pick_verifier`` prefers ``custom`` then ``re_arc``; failing both it picks
uniformly at random among the task's remaining valid slots.  A census that
probes one verifier per task therefore cannot see a bad slot that only turns up
on some seeds -- which is exactly how a5313dff's keymoon verifier survived.

    python -m pipelines.audit_verifier_slots --dataset arc --seeds 60 --jobs 8

Writes ``experiments/verifier_slot_audit_<dataset>.json``.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

MAX_PAIRS = 400
# A verifier that never returns is as unusable as one that returns the wrong
# grid, so every call is bounded and a timeout counts against the slot.
CALL_TIMEOUT_S = 2.0


class _CallTimeout(Exception):
    pass


def _bounded(fn, grid, seconds: float):
    """Call *fn* on a private copy of *grid*, bounded in time.

    The copy is not optional: some keymoon verifiers rewrite the grid they are
    handed, so a shared input would be destroyed for whichever slot is measured
    next.  Every call site in the framework deep-copies for the same reason.
    """
    import copy
    import signal

    grid = copy.deepcopy(grid)

    def _fire(signum, frame):
        raise _CallTimeout()

    fired: list = []

    def _mark(signum, frame):
        fired.append(True)
        _fire(signum, frame)

    old = signal.signal(signal.SIGALRM, _mark)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        out = fn(grid)
        # Several verifiers catch broadly enough to swallow the timeout and
        # return a half-built grid. Scoring that as a wrong answer would blame
        # the verifier for the clock, so the flag wins over the return value.
        return (None, "timeout") if fired else (out, None)
    except _CallTimeout:
        return None, "timeout"
    except BaseException as exc:
        return None, "timeout" if fired else type(exc).__name__
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def _audit_one(payload) -> Dict[str, Any]:
    task_id, dataset, seeds, timeout_s = payload
    from framework.tasks.arc_dataset import load_task
    from framework.active_arc.verifier_selection import list_valid_verifiers

    out: Dict[str, Any] = {"task_id": task_id, "slots": {}}
    try:
        task = load_task(task_id)
    except Exception as exc:
        out["error"] = "load: %s" % exc
        return out
    gen = task.arc_gen_generator
    if gen is None:
        out["error"] = "no generator"
        return out
    try:
        valid = list_valid_verifiers(task)
    except Exception as exc:
        out["error"] = "slots: %s" % exc
        return out
    if not valid:
        out["error"] = "no valid verifier"
        return out

    # One draw of pairs, shared by every slot, so the slots are compared on
    # exactly the same evidence. The generator's argument is a pair *count*, not
    # a seed -- asking for n in a loop would draw n(n-1)/2 pairs to keep n.
    pairs = []
    try:
        pairs = [(p.input, p.output) for p in gen(seeds)]
    except Exception:
        for _ in range(4):          # a sampler that gives up sometimes
            try:
                pairs.extend((p.input, p.output) for p in gen(max(seeds // 4, 1)))
            except Exception:
                continue
    pairs = pairs[:MAX_PAIRS]
    official = [(p.input, p.output) for p in task.train_pairs] + \
               list(zip(task.test_inputs, task.test_outputs))
    out["n_pairs"] = len(pairs)
    out["n_official"] = len(official)

    # Several slots share the name "custom" (the local verifier and the vendored
    # ARC-AGI-2 candidates), so they are keyed by position as pick_verifier sees
    # them -- that index is what gets pinned.
    for idx, (slot, fn) in enumerate(valid):
        bad = err = slow = 0
        first = None
        for gi, go in pairs:
            got, why = _bounded(fn, gi, timeout_s)
            if why is not None:
                err += 1
                slow += (why == "timeout")
                first = first or why
                continue
            if got != go:
                bad += 1
        off_ok = 0
        for gi, go in official:
            got, why = _bounded(fn, gi, timeout_s)
            if why is None and got == go:
                off_ok += 1
        out["slots"]["%d:%s" % (idx, slot)] = {
            "slot": slot, "index": idx, "mismatched": bad, "errored": err,
            "timeouts": slow, "first_error": first, "official_ok": off_ok,
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", choices=("arc", "arc2"), default="arc")
    ap.add_argument("--seeds", type=int, default=MAX_PAIRS,
                    help="pairs to draw (the generator argument is a count, not a seed)")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--task-id", action="append", default=None)
    ap.add_argument("--call-timeout-s", type=float, default=CALL_TIMEOUT_S)
    args = ap.parse_args()

    if args.task_id:
        ids = list(args.task_id)
    elif args.dataset == "arc":
        from framework.tasks.arc_dataset import list_arc_agi_1_task_ids
        ids = list(list_arc_agi_1_task_ids())
    else:
        from framework.integrations.agi2_verifiers import _index
        ids = sorted(_index().keys())

    payloads = [(t, args.dataset, args.seeds, args.call_timeout_s) for t in ids]
    rows: List[Dict[str, Any]] = []
    # A --task-id probe writes to its own files: the full census is the artefact
    # apply_canon_verifiers and rerun_impact read, and a probe of two tasks must
    # not truncate it (which is exactly what happened once).
    suffix = "_subset" if args.task_id else ""
    out = ROOT_DIR / "experiments" / ("verifier_slot_audit_%s%s.json" % (args.dataset, suffix))
    # Appended as they land: one stuck task must not cost the whole pass.
    stream = out.with_suffix(".jsonl")
    stream.write_text("", encoding="utf-8")
    ctx = mp.get_context("spawn")
    with ctx.Pool(processes=args.jobs) as pool:
        for i, row in enumerate(pool.imap_unordered(_audit_one, payloads), start=1):
            rows.append(row)
            with stream.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row) + "\n")
            flagged = [k for k, v in (row.get("slots") or {}).items()
                       if v["mismatched"] or v["errored"] or v["official_ok"] < row.get("n_official", 0)]
            mark = ("  FLAG " + ",".join(flagged)) if flagged else ""
            print("[%d/%d] %s%s" % (i, len(payloads), row["task_id"], mark), flush=True)

    out.write_text(json.dumps({"dataset": args.dataset, "seeds": args.seeds,
                               "max_pairs": MAX_PAIRS, "rows": rows}, indent=1), encoding="utf-8")
    n_flag = sum(1 for r in rows
                 for v in (r.get("slots") or {}).values()
                 if v["mismatched"] or v["errored"] or v["official_ok"] < r.get("n_official", 0))
    print("wrote %s | %d task-slot combinations flagged" % (out, n_flag))


if __name__ == "__main__":
    main()
