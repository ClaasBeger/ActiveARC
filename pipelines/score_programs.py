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

SKIP_FILES = {"manifest.json", "summary.json", "program_scores.json"}


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
        "--write",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Write results back into the trial JSONs (default: true).",
    )
    return p.parse_args()


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
    for i, path in enumerate(paths, 1):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[{i}/{len(paths)}] {path.name}: unreadable ({e})", flush=True)
            continue
        trial = record.get("trial") or {}
        task_id = record.get("task_id", path.stem)
        code: Optional[str] = trial.get("program_source")

        if args.skip_scored and trial.get("program_eval"):
            print(f"[{i}/{len(paths)}] {task_id}: already scored", flush=True)
            rows.append({"task_id": task_id, "skipped": True, "correct": record.get("correct")})
            continue
        if not code:
            print(f"[{i}/{len(paths)}] {task_id}: no program recorded", flush=True)
            rows.append({"task_id": task_id, "no_program": True})
            continue

        seed = args.seed if args.seed is not None else int(record.get("seed") or 0)
        try:
            task = _load_task(record)
        except Exception as e:
            print(f"[{i}/{len(paths)}] {task_id}: task load failed ({type(e).__name__}: {e})", flush=True)
            rows.append({"task_id": task_id, "error": f"{type(e).__name__}: {e}"})
            continue

        report = evaluate_program(
            task,
            code,
            rng=random.Random(seed),
            dynamic_n=args.dynamic_n,
            call_timeout_s=args.call_timeout_s,
        )
        result = report.to_dict()
        sets = " ".join(f"{k}={v['n_correct']}/{v['n']}" for k, v in result["sets"].items())
        print(
            f"[{i}/{len(paths)}] {task_id}: correct={result['all_correct']} {sets}"
            + ("" if report.loaded else f" load_error={report.error}"),
            flush=True,
        )

        if args.write:
            trial["program_eval"] = result
            trial["program_eval_deferred"] = False
            record["trial"] = trial
            record["correct"] = result["all_correct"]
            path.write_text(json.dumps(record, indent=2), encoding="utf-8")

        rows.append(
            {
                "task_id": task_id,
                "correct": result["all_correct"],
                "loaded": result["loaded"],
                "accuracy": result["accuracy"],
                "n_total": result["n_total"],
                "query_count": record.get("query_count"),
                "sets": {k: [v["n_correct"], v["n"]] for k, v in result["sets"].items()},
            }
        )

    scored = [r for r in rows if "correct" in r and not r.get("skipped")]
    n_correct = sum(1 for r in scored if r.get("correct"))
    n_loaded = sum(1 for r in scored if r.get("loaded"))
    summary = {
        "scored_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "dynamic_n": args.dynamic_n,
        "seed": args.seed,
        "n_records": len(paths),
        "n_scored": len(scored),
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
