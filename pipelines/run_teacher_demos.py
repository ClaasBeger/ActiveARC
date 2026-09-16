#!/usr/bin/env python3
"""Collect each task's teacher-chosen demonstrations, for scoring separately.

Stage one of the matched teaching comparison. A teacher that knows the rule
picks K demonstrations -- K being the task's authored pair count, so the set is
the same size as the one the static arm is shown. Nothing is scored here; the
pairs are written out and ``run_static_batch --pair-source teacher`` answers the
same held-out items from them that it answers from the authored ones.

Keeping the two stages apart is what makes the comparison mean anything: both
sets reach the same evaluator, the same items, the same prompt, so the only
thing that differs is who chose the pairs.

    python -m pipelines.run_teacher_demos --dataset arc --limit 400 \\
        --model gpt-6-astra --out-dir experiments/runs/teachK_arc400_astra
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from framework.inverse_query.session import create_inverse_query_session
from framework.prompting.clients import PROVIDERS, resolve_target
from framework.prompting.clients import build_client, resolve_model, resolve_provider, resolve_store
from framework.prompting.teacher_demos import collect_teacher_demos, run_teacher_exam
from framework.tasks.eval_items import sampled_item
from pipelines.run_active_arc_batch import _is_completed_record, _output_basename, _task_ids
from pipelines.run_static_batch import load_official


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Collect teacher-chosen demonstration sets")
    p.add_argument("--dataset", choices=["arc", "arc2", "conceptarc", "parc"], default="arc")
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--per-concept-limit", type=int, default=None)
    p.add_argument("--task-id", action="append", dest="task_ids", default=None)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out-dir", type=str, required=True)
    p.add_argument("--model", type=str, default=None)
    p.add_argument("--provider", choices=list(PROVIDERS), default=None)
    p.add_argument("--reasoning-effort", type=str, default="low")
    p.add_argument("--max-turns", type=int, default=32)
    p.add_argument(
        "--n-demos",
        type=str,
        default="auto",
        metavar="auto|N",
        help="How many demonstrations the teacher must show. 'auto' uses the task's "
        "own authored pair count, matching what the static arm is shown.",
    )
    p.add_argument(
        "--probes",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Let the teacher query a student before choosing (default: off). Off keeps "
        "the teacher's information equal to the ARC author's, who had no learner to ask.",
    )
    p.add_argument(
        "--exam",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Check the teacher on the items the solver will face before it teaches, "
        "then reset its context (default: on). A teacher that fails did not have "
        "the rule, so its set says nothing about how a rule-aware model chooses.",
    )
    p.add_argument("--skip-existing", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def _n_demos_for(args: argparse.Namespace, task_id: str) -> int:
    if str(args.n_demos).lower() == "auto":
        return len(load_official(args.dataset, task_id).train_pairs)
    return max(1, int(args.n_demos))


def _run_one(args: argparse.Namespace, task_id: str) -> dict:
    n = _n_demos_for(args, task_id)
    session = create_inverse_query_session(
        seed=args.seed, task_id=task_id, dataset=args.dataset,
    )
    session.max_demonstrations = n
    session.allow_probes = bool(args.probes)

    effort = None if args.reasoning_effort.lower() == "none" else args.reasoning_effort
    exam = None
    if args.exam:
        task = load_official(args.dataset, task_id)
        items = list(zip(task.test_inputs, task.test_outputs))
        got = sampled_item(args.dataset, args.seed, task_id)
        if got is not None:
            items.append((got[0], got[1]))
        provider = resolve_provider(args.provider, args.model)
        exam = run_teacher_exam(
            build_client(provider), session, items,
            model=resolve_model(provider, args.model), provider=provider,
            reasoning_effort=effort, store=resolve_store(provider, True),
        )
        # Teaching starts from a fresh session: nothing of the exam carries over.
        session = create_inverse_query_session(
            seed=args.seed, task_id=task_id, dataset=args.dataset,
        )
        session.max_demonstrations = n
        session.allow_probes = bool(args.probes)

    result = collect_teacher_demos(
        session,
        model=args.model,
        provider=args.provider,
        reasoning_effort=None if args.reasoning_effort.lower() == "none" else args.reasoning_effort,
        max_turns=args.max_turns,
    )
    return {
        "setting": "teacher_demos",
        "task_id": task_id,
        "dataset": args.dataset,
        "seed": args.seed,
        "n_demos_target": n,
        "probes_allowed": bool(args.probes),
        "teacher_exam": exam,
        "teacher_exam_passed": (exam or {}).get("passed"),
        **result,
    }


def main() -> None:
    args = _parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    task_ids = _task_ids(args)
    if not task_ids:
        raise SystemExit("No task ids selected.")

    target = resolve_target(provider=args.provider, model=args.model)
    args.provider, args.model = target["provider"], target["model"]

    (out_dir / "manifest.json").write_text(json.dumps({
        "started_at": datetime.now(timezone.utc).isoformat(),
        "setting": "teacher_demos",
        "dataset": args.dataset, "seed": args.seed,
        "model": args.model, "provider": args.provider,
        "reasoning_effort": args.reasoning_effort,
        "n_demos": args.n_demos, "probes_allowed": bool(args.probes),
        "task_ids": task_ids,
    }, indent=2), encoding="utf-8")

    rows = []
    t0 = time.perf_counter()
    for i, task_id in enumerate(task_ids, start=1):
        out_path = out_dir / f"{_output_basename(task_id)}.json"
        if args.skip_existing and _is_completed_record(out_path):
            print(f"[{i}/{len(task_ids)}] skip existing {task_id}", flush=True)
            continue
        started = time.perf_counter()
        print(f"[{i}/{len(task_ids)}] teaching {task_id} ...", flush=True)
        try:
            rec = _run_one(args, task_id)
            rec["elapsed_s"] = round(time.perf_counter() - started, 3)
            out_path.write_text(json.dumps(rec, indent=2), encoding="utf-8")
            rows.append({"task_id": task_id, "ok": True,
                         "n_demonstrations": rec["n_demonstrations"],
                         "target": rec["n_demos_target"], "reason": rec["reason"],
                         "exam_passed": rec.get("teacher_exam_passed")})
            ex = rec.get("teacher_exam") or {}
            exs = f" exam={ex.get('n_correct')}/{ex.get('n_items')}" if ex else ""
            print(f"  ok demos={rec['n_demonstrations']}/{rec['n_demos_target']} "
                  f"failed_shows={rec['n_failed_show']}{exs} reason={rec['reason']}", flush=True)
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
            out_path.write_text(json.dumps({
                "task_id": task_id, "seed": args.seed, "error": err,
                "traceback": traceback.format_exc(),
            }, indent=2), encoding="utf-8")
            rows.append({"task_id": task_id, "ok": False, "error": err})
            print(f"  ERR {task_id}: {err}", flush=True)

    summary = {
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_s": round(time.perf_counter() - t0, 3),
        "n_tasks": len(task_ids),
        "n_ok": sum(1 for r in rows if r.get("ok")),
        "n_error": sum(1 for r in rows if r.get("ok") is False),
        "n_complete_sets": sum(1 for r in rows if r.get("ok")
                               and r.get("n_demonstrations") == r.get("target")),
        "n_exam_passed": sum(1 for r in rows if r.get("exam_passed")),
        "n_exam_failed": sum(1 for r in rows if r.get("ok") and r.get("exam_passed") is False),
        "rows": rows,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2), flush=True)


if __name__ == "__main__":
    sys.exit(main())
