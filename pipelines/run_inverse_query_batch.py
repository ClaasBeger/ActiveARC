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
    p.add_argument("--teacher-model", type=str, default=None,
                   help="Teacher model (default: --model).")
    p.add_argument("--student-model", type=str, default=None,
                   help="Student model (default: --model).")
    p.add_argument(
        "--teacher-check",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Draw the exam first and make the teacher solve every item from its own "
             "briefing; a trial whose teacher cannot is recorded and skipped.",
    )
    p.add_argument("--sample", type=int, default=None,
                   help="Seeded random subset of this size (after --exclude-task-id), "
                        "instead of --offset/--limit. ConceptARC samples the 160 official tasks.")
    p.add_argument("--exclude-task-id", action="append", default=[],
                   help="Task id to leave out (repeatable).")
    p.add_argument("--task-id", action="append", dest="task_ids", default=None,
                   help="Run exactly these task ids (repeatable); overrides --sample/--offset/--limit.")
    p.add_argument("--dry-run", action="store_true",
                   help="Print the selected task ids and exit.")
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
        teacher_model=args.teacher_model,
        student_model=args.student_model,
        teacher_check=args.teacher_check,
        max_turns=args.max_turns,
        student_max_turns=args.student_max_turns,
        reasoning_effort=reasoning_effort,
    )
    return build_inverse_query_record(session, result)


def _select_task_ids(args: argparse.Namespace) -> list[str]:
    """--sample draws a seeded subset of the whole pool; otherwise offset/limit as before."""
    import random

    if args.task_ids:
        excluded = set(args.exclude_task_id or [])
        return [t for t in args.task_ids if t not in excluded]
    if args.sample is None:
        id_args = SimpleNamespace(
            dataset=args.dataset, offset=args.offset, limit=args.limit,
            per_concept_limit=args.per_concept_limit, task_ids=None,
        )
        ids = _task_ids(id_args)
    else:
        pool_args = SimpleNamespace(
            dataset=args.dataset, offset=0, limit=10**9,
            per_concept_limit=None, task_ids=None,
        )
        ids = _task_ids(pool_args)
        if args.dataset == "conceptarc":
            # The generated families (11+) are not the benchmark; sample the
            # hand-authored 1-10 of each concept.
            def _num(t: str) -> int:
                name = t.split("/", 1)[-1]
                i = len(name)
                while i and name[i - 1].isdigit():
                    i -= 1
                return int(name[i:] or 0)
            ids = [t for t in ids if 1 <= _num(t) <= 10]
        excluded = set(args.exclude_task_id or [])
        ids = [t for t in ids if t not in excluded]
        if args.sample > len(ids):
            raise SystemExit(f"--sample {args.sample} exceeds the {len(ids)} eligible tasks.")
        ids = sorted(random.Random(args.seed).sample(ids, args.sample))
    excluded = set(args.exclude_task_id or [])
    return [t for t in ids if t not in excluded]


def main() -> None:
    args = _parse_args()
    task_ids = _select_task_ids(args)
    if not task_ids:
        raise SystemExit("No task ids selected.")
    if args.dry_run:
        print(json.dumps({"dataset": args.dataset, "n": len(task_ids), "task_ids": task_ids}, indent=1))
        return

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "setting": "inverse_query",
        "dataset": args.dataset,
        "model": args.model or DEFAULT_OPENAI_MODEL,
        "teacher_model": args.teacher_model or args.model or DEFAULT_OPENAI_MODEL,
        "student_model": args.student_model or args.model or DEFAULT_OPENAI_MODEL,
        "teacher_check": args.teacher_check,
        "sample": args.sample,
        "explicit_task_ids": list(args.task_ids or []),
        "exclude_task_id": list(args.exclude_task_id or []),
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
                "teacher_check_passed": (record.get("teacher_check") or {}).get("passed"),
                "teacher_check_n_correct": (record.get("teacher_check") or {}).get("n_correct"),
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
            if row.get("final_reason") == "teacher_failed_check":
                extra = (f" TEACHER FAILED CHECK {row.get('teacher_check_n_correct')}/{row.get('exam_n')}"
                         " -- trial skipped")
            else:
                extra = (
                    f" exam={row.get('exam_correct')}/{row.get('exam_n')}"
                    f" shows={row.get('n_show_pair')} probes={row.get('n_query_student')}"
                )
                if row.get("teacher_check_passed") is not None:
                    extra += f" teacher_check={'pass' if row['teacher_check_passed'] else 'fail'}"
        print(f"[{i}/{len(task_ids)}] {status} {task_id}{extra}", flush=True)

    n_ok = sum(1 for r in rows if r.get("ok") is True)
    n_err = sum(1 for r in rows if r.get("ok") is False)
    n_skip = sum(1 for r in rows if r.get("skipped"))
    taught = [r for r in rows if r.get("ok") and r.get("final_reason") != "teacher_failed_check"]
    exam_scores = [r["exam_score"] for r in taught if isinstance(r.get("exam_score"), (int, float))]
    n_teacher_failed = sum(1 for r in rows if r.get("final_reason") == "teacher_failed_check")
    summary = {
        "n_teacher_failed_check": n_teacher_failed,
        "teacher_failed_check_task_ids": sorted(r["task_id"] for r in rows
                                                if r.get("final_reason") == "teacher_failed_check"),
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
        f"teacher_failed_check={n_teacher_failed} "
        f"mean_exam_score(taught only)={summary['mean_exam_score']}",
        flush=True,
    )


if __name__ == "__main__":
    main()
