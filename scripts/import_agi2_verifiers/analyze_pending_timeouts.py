#!/usr/bin/env python3
"""Isolated analysis of pending_timeout AGI-2 verifier candidates."""

from __future__ import annotations

import contextlib
import importlib.util
import json
import multiprocessing as mp
import os
import random
import signal
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.import_agi2_verifiers.paths import ARC_ORIGINAL, CANDIDATES, LOGS


def worker(payload: dict, q) -> None:
    import framework.tasks.arc_dataset as ad
    from scripts.import_agi2_verifiers.grid_utils import (
        deep_copy_grid,
        grids_equal,
        load_official_pairs,
        to_grid,
    )

    class Alarm(Exception):
        pass

    def handler(signum, frame):  # noqa: ARG001
        raise Alarm()

    def with_timeout(seconds, fn, *a, **k):
        old = signal.signal(signal.SIGALRM, handler)
        try:
            signal.setitimer(signal.ITIMER_REAL, seconds)
            t0 = time.perf_counter()
            out = fn(*a, **k)
            dt = time.perf_counter() - t0
            return "ok", out, dt, None
        except Alarm:
            return "timeout", None, seconds, None
        except Exception as e:
            return "exception", None, None, f"{type(e).__name__}:{e}"
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old)

    tid = payload["task_id"]
    rel = payload["relative_path"]
    cid = payload["candidate_id"]
    result: dict = {"candidate_id": cid, "task_id": tid, "source": payload.get("source")}

    lookup = ad._arc_gen_id_to_task_num_and_generator(tid)
    if lookup is None:
        result["classification"] = "no_generator"
        q.put(result)
        return
    _, gen = lookup

    gen_times = []
    gen_pairs = []
    gen_fails = 0
    gen_timeouts = 0
    seed = 0
    while len(gen_pairs) < 5 and seed < 200:
        st = random.getstate()
        try:
            random.seed(seed)
            status, ex, dt, err = with_timeout(5.0, gen)
            if status == "ok":
                inp, out = to_grid(ex["input"]), to_grid(ex["output"])
                if inp and out:
                    gen_pairs.append((inp, out))
                    gen_times.append(dt)
                else:
                    gen_fails += 1
            elif status == "timeout":
                gen_timeouts += 1
                if seed == 0:
                    result["gen0_err"] = "timeout>5s"
            else:
                gen_fails += 1
                if seed == 0:
                    result["gen0_err"] = err
        finally:
            random.setstate(st)
        seed += 1

    result["gen_ok"] = len(gen_pairs)
    result["gen_fails"] = gen_fails
    result["gen_timeouts"] = gen_timeouts
    result["gen_max_s"] = max(gen_times) if gen_times else None
    result["seeds_tried"] = seed

    if not gen_pairs:
        result["classification"] = (
            "stuck_in_generator" if gen_timeouts else "generator_broken"
        )
        q.put(result)
        return

    path = CANDIDATES / rel
    spec = importlib.util.spec_from_file_location("cand", path)
    mod = importlib.util.module_from_spec(spec)
    try:
        with open(os.devnull, "w") as d, contextlib.redirect_stdout(d), contextlib.redirect_stderr(d):
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
        fn = mod.verify
    except Exception as e:
        result["classification"] = "invalid_load"
        result["detail"] = f"{type(e).__name__}:{e}"
        q.put(result)
        return

    pairs = load_official_pairs(json.loads((ARC_ORIGINAL / f"{tid}.json").read_text()))
    off_t = []
    for split, i, inp, exp in pairs:
        status, out, dt, err = with_timeout(10.0, fn, deep_copy_grid(inp))
        if status != "ok":
            result["classification"] = "stuck_or_fail_on_official"
            result["detail"] = f"{split}[{i}]:{status}:{err}"
            q.put(result)
            return
        if not grids_equal(out, exp):
            result["classification"] = "invalid_official"
            result["detail"] = f"{split}[{i}]:incorrect"
            q.put(result)
            return
        off_t.append(dt)
    result["official_max_s"] = max(off_t)

    dyn_times = []
    for j, (inp, exp) in enumerate(gen_pairs):
        status, out, dt, err = with_timeout(30.0, fn, deep_copy_grid(inp))
        if status == "timeout":
            result["classification"] = "stuck_on_dynamic_verify"
            result["detail"] = f"dynamic[{j}] timeout>30s"
            result["dyn_ok"] = j
            q.put(result)
            return
        if status != "ok":
            result["classification"] = "invalid_dynamic"
            result["detail"] = f"dynamic[{j}]:{status}:{err}"
            q.put(result)
            return
        if not grids_equal(out, exp):
            result["classification"] = "invalid_dynamic"
            result["detail"] = f"dynamic[{j}]:incorrect"
            q.put(result)
            return
        dyn_times.append(dt)

    result["dyn_ok"] = len(dyn_times)
    result["dyn_max_s"] = max(dyn_times)
    result["dyn_sum_s"] = sum(dyn_times)
    result["est_250_s"] = (sum(dyn_times) / len(dyn_times)) * 250
    if result["dyn_max_s"] >= 2.0 or result["est_250_s"] >= 120:
        result["classification"] = "slow_but_likely_ok"
    else:
        result["classification"] = "fast_on_sample"
    q.put(result)


def run_one(meta: dict, overall: float = 90.0) -> dict:
    ctx = mp.get_context("spawn")
    q: mp.Queue = ctx.Queue()
    p = ctx.Process(target=worker, args=(meta, q))
    p.start()
    p.join(overall)
    if p.is_alive():
        p.terminate()
        p.join(3)
        if p.is_alive():
            p.kill()
            p.join(1)
        return {
            "candidate_id": meta["candidate_id"],
            "task_id": meta["task_id"],
            "source": meta.get("source"),
            "classification": "hard_stuck_process",
            "detail": f"worker>{overall}s",
        }
    try:
        return q.get_nowait()
    except Exception as e:
        return {
            "candidate_id": meta["candidate_id"],
            "classification": "no_result",
            "detail": str(e),
        }


def main() -> int:
    pending = [
        r
        for r in json.loads((LOGS / "final_results.json").read_text())
        if r.get("status") == "pending_timeout"
    ]
    print(f"n={len(pending)}", flush=True)
    results = []
    for i, m in enumerate(pending, 1):
        r = run_one(m, overall=90.0)
        results.append(r)
        print(
            f"[{i}/{len(pending)}] {r.get('candidate_id')}: {r.get('classification')} "
            f"gen_ok={r.get('gen_ok')} gen_to={r.get('gen_timeouts')} gen_fail={r.get('gen_fails')} "
            f"dyn_max={r.get('dyn_max_s')} est250={r.get('est_250_s')} "
            f"{r.get('detail') or r.get('gen0_err') or ''}",
            flush=True,
        )

    print("\n=== SUMMARY ===", flush=True)
    print(dict(Counter(r["classification"] for r in results)), flush=True)
    by_src: dict = {}
    for r in results:
        src = (r.get("source") or "").split(":")[0] or "?"
        by_src.setdefault(src, Counter())[r["classification"]] += 1
    print("By source:", flush=True)
    for src, c in sorted(by_src.items()):
        print(f"  {src}: {dict(c)}", flush=True)

    out = LOGS / "pending_timeout_isolated_analysis.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
