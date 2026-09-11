#!/usr/bin/env python3
"""Batch Inverse Query Generation (teacher + student) over a dataset.

Example::

    python -m pipelines.run_inverse_query_batch --dataset parc --limit 50 --seed 0 \\
        --out-dir experiments/runs/iq_parc50_seed0
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from framework.inverse_query.records import build_inverse_query_record
from framework.inverse_query.session import create_inverse_query_session
from framework.prompting.active_arc_tools import DEFAULT_OPENAI_MODEL
from framework.prompting.inverse_query_responses import run_inverse_query_responses_loop
from pipelines.run_active_arc_batch import _output_basename, _task_ids


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Batch Inverse Query Generation")
    p.add_argument(
        "--dataset",
        choices=["arc", "arc2", "conceptarc", "parc"],
        default="arc",
    )
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--per-concept-limit", type=int, default=None)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out-dir", type=str, required=True)
    p.add_argument("--exam-n", type=int, default=10)
    p.add_argument(
        "--model",
        type=str,
        default=None,
        help=f"OpenAI model name (default: env OPENAI_MODEL or {DEFAULT_OPENAI_MODEL}).",
    )
    p.add_argument("--max-turns", type=int, default=64)
    p.add_argument("--student-max-turns", type=int, default=8)
    p.add_argument("--reasoning-effort", type=str, default="low")
    p.add_argument("--skip-existing", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument(
        "--teacher-sample",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Give the teacher one compact generator sample (not shown to the student). Default: on.",
    )
    return p.parse_args()


def _run_one(args: argparse.Namespace, task_id: str) -> dict:
    session = create_inverse_query_session(
        seed=args.seed,
        task_id=task_id,
        dataset=args.dataset,
        exam_n=args.exam_n,
        include_teacher_sample=args.teacher_sample,
    )
    reasoning_effort = None if args.reasoning_effort.lower() == "none" else args.reasoning_effort
    result = run_inverse_query_responses_loop(
        session,
        model=args.model,
        max_turns=args.max_turns,
        student_max_turns=args.student_max_turns,
        reasoning_effort=reasoning_effort,
    )
    return build_inverse_query_record(session, result)


def main() -> None:
    args = _parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    id_args = SimpleNamespace(
        dataset=args.dataset,
        offset=args.offset,
        limit=args.limit,
        per_concept_limit=args.per_concept_limit,
    )
    task_ids = _task_ids(id_args)
    if not task_ids:
        raise SystemExit("No task ids selected.")

    manifest = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "setting": "inverse_query",
        "dataset": args.dataset,
        "model": args.model or DEFAULT_OPENAI_MODEL,
        "reasoning_effort": args.reasoning_effort,
        "seed": args.seed,
        "exam_n": args.exam_n,
        "teacher_sample": args.teacher_sample,
        "offset": args.offset,
        "limit": args.limit,
        "per_concept_limit": args.per_concept_limit,
        "task_ids": task_ids,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    summary_path = out_dir / "summary.jsonl"
    rows: list[dict] = []
    t0 = time.perf_counter()

    for i, task_id in enumerate(task_ids, start=1):
        out_path = out_dir / f"{_output_basename(task_id)}.json"
        if args.skip_existing and out_path.is_file():
            print(f"[{i}/{len(task_ids)}] skip existing {task_id}", flush=True)
            try:
                existing = json.loads(out_path.read_text(encoding="utf-8"))
                row = {
                    "task_id": task_id,
                    "skipped": True,
                    "exam_correct": existing.get("exam_correct"),
                    "exam_n": existing.get("exam_n"),
                    "exam_score": existing.get("exam_score"),
                    "n_show_pair": existing.get("n_show_pair"),
                    "n_query_student": existing.get("n_query_student"),
                }
                rows.append(row)
                with summary_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(row) + "\n")
            except Exception:
                pass
            continue

        print(f"[{i}/{len(task_ids)}] running {task_id} ...", flush=True)
        started = time.perf_counter()
        try:
            record = _run_one(args, task_id)
            record["elapsed_s"] = round(time.perf_counter() - started, 3)
            out_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
            row = {
                "task_id": task_id,
                "ok": True,
                "exam_correct": record.get("exam_correct"),
                "exam_n": record.get("exam_n"),
                "exam_score": record.get("exam_score"),
                "n_show_pair": record.get("n_show_pair"),
                "n_query_student": record.get("n_query_student"),
                "n_demonstrations": record.get("n_demonstrations"),
                "turns": len(record.get("teacher_transcript") or []),
                "usage": record.get("usage"),
                "elapsed_s": record["elapsed_s"],
                "final_reason": (record.get("final") or {}).get("reason"),
            }
            status = "ok"
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
            tb = traceback.format_exc()
            record = {
                "task_id": task_id,
                "seed": args.seed,
                "error": err,
                "traceback": tb,
                "elapsed_s": round(time.perf_counter() - started, 3),
            }
            out_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
            row = {
                "task_id": task_id,
                "ok": False,
                "error": err,
                "elapsed_s": record["elapsed_s"],
            }
            status = "ERROR"
        rows.append(row)
        with summary_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        extra = ""
        if row.get("ok"):
            extra = (
                f" exam={row.get('exam_correct')}/{row.get('exam_n')}"
                f" shows={row.get('n_show_pair')} probes={row.get('n_query_student')}"
            )
        print(f"[{i}/{len(task_ids)}] {status} {task_id}{extra}", flush=True)

    n_ok = sum(1 for r in rows if r.get("ok") is True)
    n_err = sum(1 for r in rows if r.get("ok") is False)
    n_skip = sum(1 for r in rows if r.get("skipped"))
    exam_scores = [r["exam_score"] for r in rows if isinstance(r.get("exam_score"), (int, float))]
    summary = {
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_s": round(time.perf_counter() - t0, 3),
        "n_tasks": len(task_ids),
        "n_ok": n_ok,
        "n_error": n_err,
        "n_skipped": n_skip,
        "mean_exam_score": (sum(exam_scores) / len(exam_scores)) if exam_scores else None,
        "rows": rows,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(
        f"done n_ok={n_ok} n_error={n_err} n_skipped={n_skip} "
        f"mean_exam_score={summary['mean_exam_score']}",
        flush=True,
    )


if __name__ == "__main__":
    main()
