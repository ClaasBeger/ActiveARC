#!/usr/bin/env python3
"""Score programs recorded by ``--program-test --defer-program-eval`` runs.

Reads each trial JSON in a run directory, evaluates its ``program_source`` against
train / test / generator-stable / generator-dynamic, and writes the result back
into the record (plus a ``program_scores.json`` summary)::

    python -m pipelines.score_programs experiments/runs/prog_arc_agi_1_astra_seed0

Re-running rescores from scratch unless ``--skip-scored`` is given, so a run can be
scored again later against a different evaluation suite.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from framework.active_arc.program_eval import DEFAULT_DYNAMIC_N, evaluate_program

SKIP_FILES = {"manifest.json", "summary.json", "summary.jsonl", "program_scores.json",
              "oracle_recheck.json", "oracle_recheck_canon.json", "INVALID.json"}


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Score recorded ActiveARC programs")
    p.add_argument("run_dir", type=str, help="Run directory containing per-task JSONs.")
    p.add_argument(
        "--dynamic-n",
        type=int,
        default=DEFAULT_DYNAMIC_N,
        help=f"Fresh generator pairs to draw per task (default {DEFAULT_DYNAMIC_N}).",
    )
    p.add_argument(
        "--call-timeout-s",
        type=float,
        default=2.0,
        help="Wall-clock cap per program call (default 2.0).",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=None,
        help="RNG seed for the dynamic draw (default: each trial's own seed).",
    )
    p.add_argument(
        "--skip-scored",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Leave records that already carry a program_eval untouched.",
    )
    p.add_argument(
        "--guard",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Drop evaluation pairs the task verifier cannot reproduce "
        "(framework.tasks.pair_guard). On by default; --no-guard scores against "
        "raw generator labels.",
    )
    p.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="Score this many trials in parallel (default 1).",
    )
    p.add_argument(
        "--write",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Write results back into the trial JSONs (default: true).",
    )
    return p.parse_args()


STABLE_DIR = ROOT_DIR / "experiments" / "stable_sets"


def _safe_name(task_id: str) -> str:
    return task_id.replace("/", "__")


def _frozen_set(dataset: str, task_id: str):
    """The frozen evaluation set for this task, and whether it exhausts its generator.

    Returns ``(pairs, exhausted, n_distinct)`` or ``(None, False, 0)`` when the
    task has no frozen set and the committed pool should stand in.
    """
    import gzip

    from framework.grids import GridPair

    base = STABLE_DIR / dataset / _safe_name(task_id)
    for path, opener in ((base.with_suffix(".json.gz"), gzip.open),
                         (base.with_suffix(".json"), open)):
        if not path.is_file():
            continue
        with opener(path, "rt", encoding="utf-8") as fh:
            data = json.load(fh)
        pairs = data["pairs"] if isinstance(data, dict) else data
        meta = data if isinstance(data, dict) else {}
        return ([GridPair(p["input"], p["output"]) for p in pairs],
                bool(meta.get("exhausted")), len(pairs))
    return None, False, 0


def _task_verifier(record: Dict[str, Any], task):
    """The oracle the trial queried: pinned slot for ARC, custom for the rest."""
    dataset = record.get("dataset", "arc")
    if dataset in ("parc", "conceptarc"):
        return task.quinary_verifier or task.verifier
    from framework.active_arc.verifier_selection import list_valid_verifiers

    slot = (record.get("trial") or {}).get("verifier_slot")
    valid = list_valid_verifiers(task)
    for s, fn in valid:
        if s == slot:
            return fn
    return valid[0][1] if valid else task.verifier


def _load_task(record: Dict[str, Any]):
    dataset = record.get("dataset", "arc")
    task_id = str(record.get("task_id"))
    if dataset == "parc":
        from framework.tasks.parc_dataset import load_parc_task

        return load_parc_task(task_id)
    if dataset == "conceptarc":
        from framework.integrations.conceptarc_adapter import load_conceptarc_task

        return load_conceptarc_task(task_id)
    from framework.tasks.arc_dataset import load_task

    return load_task(task_id, load_alternative_verifiers=False)



def _score_one(payload: tuple) -> Dict[str, Any]:
    """Score one trial. Runs in a worker process; returns plain data only."""
    (path_str, dynamic_n, call_timeout_s, seed_override, use_guard) = payload
    path = Path(path_str)
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"path": path_str, "unreadable": f"{type(e).__name__}: {e}"}
    trial = record.get("trial") or {}
    task_id = record.get("task_id", path.stem)
    code = trial.get("program_source")
    if not code:
        return {"path": path_str, "task_id": task_id, "no_program": True}
    seed = seed_override if seed_override is not None else int(record.get("seed") or 0)
    try:
        task = _load_task(record)
    except Exception as e:
        return {"path": path_str, "task_id": task_id, "error": f"{type(e).__name__}: {e}"}
    guard = _task_verifier(record, task) if use_guard else None
    dataset = record.get("dataset", "arc")
    stable, exhausted, n_stable = _frozen_set(dataset, task_id)
    bottlenecked = bool(stable is not None and (exhausted or n_stable < dynamic_n))
    report = evaluate_program(
        task,
        code,
        rng=random.Random(seed),
        dynamic_n=dynamic_n,
        call_timeout_s=call_timeout_s,
        guard_verifier=guard,
        stable_pairs=stable,
        skip_dynamic=bottlenecked,
    )
    result = report.to_dict()
    result["stable_source"] = "frozen" if stable is not None else "committed_pool"
    result["dynamic_skipped"] = bottlenecked
    return {"path": path_str, "task_id": task_id, "result": result,
            "loaded": report.loaded, "load_error": report.error,
            "query_count": record.get("query_count")}


def main() -> None:
    args = _parse_args()
    run_dir = Path(args.run_dir)
    if not run_dir.is_dir():
        raise SystemExit(f"No such run directory: {run_dir}")

    paths = sorted(p for p in run_dir.glob("*.json") if p.name not in SKIP_FILES)
    if not paths:
        raise SystemExit(f"No trial JSONs in {run_dir}")

    rows: List[Dict[str, Any]] = []
    t0 = time.perf_counter()

    todo = []
    for path in paths:
        if args.skip_scored:
            try:
                rec = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                rec = {}
            pe = (rec.get("trial") or {}).get("program_eval")
            if pe:
                # Carry the stored evaluation into the summary in the same shape as
                # a fresh one, so a resume pass still describes the whole directory.
                rows.append({
                    "task_id": rec.get("task_id", path.stem),
                    "skipped": True,
                    "correct": pe.get("all_correct"),
                    "loaded": pe.get("loaded"),
                    "accuracy": pe.get("accuracy"),
                    "n_total": pe.get("n_total"),
                    "query_count": rec.get("query_count"),
                    "sets": {k: [v["n_correct"], v["n"]] for k, v in (pe.get("sets") or {}).items()},
                })
                continue
        todo.append((str(path), args.dynamic_n, args.call_timeout_s, args.seed, args.guard))

    def _emit(i: int, out: Dict[str, Any]) -> None:
        task_id = out.get("task_id", "?")
        if out.get("unreadable"):
            print(f"[{i}/{len(todo)}] {task_id}: unreadable ({out['unreadable']})", flush=True)
            return
        if out.get("no_program"):
            print(f"[{i}/{len(todo)}] {task_id}: no program recorded", flush=True)
            rows.append({"task_id": task_id, "no_program": True})
            return
        if out.get("error"):
            print(f"[{i}/{len(todo)}] {task_id}: task load failed ({out['error']})", flush=True)
            rows.append({"task_id": task_id, "error": out["error"]})
            return
        result = out["result"]
        sets = " ".join(f"{k}={v['n_correct']}/{v['n']}" for k, v in result["sets"].items())
        if result.get("dynamic_skipped"):
            sets += " (dynamic skipped: generator exhausted)"
        print(f"[{i}/{len(todo)}] {task_id}: correct={result['all_correct']} {sets}"
              + ("" if out.get("loaded") else f" load_error={out.get('load_error')}"), flush=True)
        if args.write:
            path = Path(out["path"])
            record = json.loads(path.read_text(encoding="utf-8"))
            trial = record.get("trial") or {}
            trial["program_eval"] = result
            trial["program_eval_deferred"] = False
            record["trial"] = trial
            record["correct"] = result["all_correct"]
            path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        rows.append({
            "task_id": task_id,
            "correct": result["all_correct"],
            "loaded": result["loaded"],
            "accuracy": result["accuracy"],
            "n_total": result["n_total"],
            "query_count": out.get("query_count"),
            "sets": {k: [v["n_correct"], v["n"]] for k, v in result["sets"].items()},
        })

    if args.jobs > 1:
        import multiprocessing as mp

        # spawn, not fork: the vendored ARC-AGI-2 verifiers import numpy, which
        # fails in a process forked from one that already loaded it.
        with mp.get_context("spawn").Pool(args.jobs) as pool:
            for i, out in enumerate(pool.imap(_score_one, todo), 1):
                _emit(i, out)
    else:
        for i, payload in enumerate(todo, 1):
            _emit(i, _score_one(payload))

    scored = [r for r in rows if "sets" in r]          # fresh this pass or carried over
    n_correct = sum(1 for r in scored if r.get("correct"))
    n_loaded = sum(1 for r in scored if r.get("loaded"))
    summary = {
        "scored_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "dynamic_n": args.dynamic_n,
        "guard": args.guard,
        "seed": args.seed,
        "n_records": len(paths),
        "n_scored": len(scored),
        "n_scored_this_pass": sum(1 for r in scored if not r.get("skipped")),
        "n_loaded": n_loaded,
        "n_correct": n_correct,
        "elapsed_s": round(time.perf_counter() - t0, 3),
        "rows": rows,
    }
    (run_dir / "program_scores.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(
        f"\nscored {len(scored)} · loaded {n_loaded} · correct {n_correct} "
        f"· {summary['elapsed_s'] / 60:.1f} min",
        flush=True,
    )


if __name__ == "__main__":
    main()
