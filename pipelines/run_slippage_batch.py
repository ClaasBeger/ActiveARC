#!/usr/bin/env python3
"""Run the ActiveARC agent on slippage trials (narrow hot start, broad discovery).

Each task runs once, with its canonical narrow slot from
``experiments/slippage/slippage_pairs.json``::

    python -m pipelines.run_slippage_batch --limit 249 --seed 0 \\
        --model gpt-6-astra --out-dir experiments/runs/slippage_astra_seed0

Writes one JSON per task plus a rolling ``summary.jsonl`` and final ``summary.json``.
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

from framework.active_arc.trial_record import build_trial_record
from framework.prompting.active_arc_openai import run_openai_agent_loop
from framework.prompting.active_arc_responses import run_active_arc_responses_loop
from framework.prompting.active_arc_tools import DEFAULT_OPENAI_MODEL
from framework.prompting.clients import PROVIDERS, resolve_target
from framework.slippage.trial import (
    canonical_narrow_slots,
    create_slippage_trial_session,
    slippage_task_ids,
)


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Batch ActiveARC slippage runs")
    p.add_argument("--limit", type=int, default=249)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--task-id", type=str, default=None, help="Run a single task id.")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out-dir", type=str, required=True)
    p.add_argument(
        "--pairs",
        type=str,
        default=None,
        help="Slippage pairs JSON (default: experiments/slippage/slippage_pairs.json).",
    )
    p.add_argument("--backend", choices=["responses", "chat"], default="responses")
    p.add_argument(
        "--provider",
        choices=list(PROVIDERS),
        default=None,
        help="Model provider; default inferred from --model, else openai.",
    )
    p.add_argument("--model", type=str, default=None)
    p.add_argument("--max-turns", type=int, default=64)
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--reasoning-effort", type=str, default="low")
    p.add_argument("--hot-start", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--noisy-science", action="store_true")
    p.add_argument("--re-trials", action=argparse.BooleanOptionalAction, default=False)
    p.add_argument("--wrong-answer-penalty", type=int, default=0, metavar="N")
    p.add_argument("--fixed-test", action=argparse.BooleanOptionalAction, default=False)
    p.add_argument("--noise-probability", type=float, default=0.12)
    p.add_argument("--skip-existing", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def _run_one(args: argparse.Namespace, task_id: str) -> dict:
    pairs_path = Path(args.pairs) if args.pairs else None
    session = create_slippage_trial_session(
        seed=args.seed,
        task_id=task_id,
        hot_start=args.hot_start,
        noisy_science=args.noisy_science,
        re_trials=args.re_trials,
        wrong_answer_penalty=args.wrong_answer_penalty,
        noise_probability=args.noise_probability,
        fixed_test=args.fixed_test,
        pairs_path=pairs_path,
    )
    reasoning_effort = None if args.reasoning_effort.lower() == "none" else args.reasoning_effort
    if args.backend == "responses":
        result = run_active_arc_responses_loop(
            session,
            model=args.model,
            max_turns=args.max_turns,
            reasoning_effort=reasoning_effort,
            provider=args.provider,
        )
    else:
        result = run_openai_agent_loop(
            session,
            model=args.model,
            max_turns=args.max_turns,
            temperature=args.temperature,
            provider=args.provider,
            reasoning_effort=reasoning_effort,
        )
    record = build_trial_record(
        session,
        result,
        dataset="arc",
        hot_start=args.hot_start,
        noisy_science=args.noisy_science,
        re_trials=args.re_trials,
        fixed_test=args.fixed_test,
    )
    record["setting"] = "slippage"
    record["trial"]["narrow_slot"] = session.narrow_slot
    record["trial"]["broad_slot"] = session.verifier_slot
    record["trial"]["hot_start_source"] = "arc_gen (narrow)"
    record["trial"]["test_source"] = "re_arc (broad)"
    record["trial"]["hot_start_broad_agrees"] = session.hot_start_broad_agrees
    return record


def _task_ids(args: argparse.Namespace) -> list[str]:
    pairs_path = Path(args.pairs) if args.pairs else None
    if args.task_id:
        return [args.task_id]
    ids = slippage_task_ids(pairs_path)
    return ids[args.offset : args.offset + args.limit]


def main() -> None:
    args = _parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    task_ids = _task_ids(args)
    if not task_ids:
        raise SystemExit("No slippage task ids selected.")
    pairs_path = Path(args.pairs) if args.pairs else None
    narrow_by_task = canonical_narrow_slots(pairs_path)

    target = resolve_target(
        provider=args.provider, model=args.model, backend=args.backend
    )
    args.provider = target["provider"]
    args.model = target["model"]
    args.backend = target["backend"]
    if target["backend_note"]:
        print(f"[provider] {target['backend_note']}")

    manifest = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "setting": "slippage",
        "dataset": "arc",
        "backend": args.backend,
        "provider": args.provider,
        "model": args.model,
        "reasoning_effort": args.reasoning_effort,
        "seed": args.seed,
        "offset": args.offset,
        "limit": args.limit,
        "task_ids": task_ids,
        "narrow_slots": {t: narrow_by_task.get(t) for t in task_ids},
        "flags": {
            "hot_start": args.hot_start,
            "noisy_science": args.noisy_science,
            "re_trials": args.re_trials,
            "fixed_test": args.fixed_test,
            "wrong_answer_penalty": args.wrong_answer_penalty,
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    summary_path = out_dir / "summary.jsonl"
    rows: list[dict] = []
    t0 = time.perf_counter()

    for i, task_id in enumerate(task_ids, start=1):
        out_path = out_dir / f"{task_id}.json"
        if args.skip_existing and out_path.is_file():
            print(f"[{i}/{len(task_ids)}] skip existing {task_id}", flush=True)
            try:
                existing = json.loads(out_path.read_text(encoding="utf-8"))
                row = {
                    "task_id": task_id,
                    "skipped": True,
                    "correct": existing.get("correct"),
                    "query_count": existing.get("query_count"),
                    "narrow_slot": (existing.get("trial") or {}).get("narrow_slot"),
                    "usage": existing.get("usage"),
                }
                rows.append(row)
                with summary_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(row) + "\n")
            except Exception:
                pass
            continue

        print(
            f"[{i}/{len(task_ids)}] running {task_id} (narrow={narrow_by_task.get(task_id)}) ...",
            flush=True,
        )
        started = time.perf_counter()
        try:
            record = _run_one(args, task_id)
            record["elapsed_s"] = round(time.perf_counter() - started, 3)
            out_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
            row = {
                "task_id": task_id,
                "ok": True,
                "correct": record.get("correct"),
                "query_count": record.get("query_count"),
                "narrow_slot": record["trial"].get("narrow_slot"),
                "hot_start_broad_agrees": record["trial"].get("hot_start_broad_agrees"),
                "turns": len(record.get("transcript") or []),
                "usage": record.get("usage"),
                "elapsed_s": record["elapsed_s"],
                "final_reason": (record.get("final") or {}).get("reason"),
            }
            print(
                f"  ok correct={row['correct']} queries={row['query_count']} "
                f"turns={row['turns']}",
                flush=True,
            )
        except Exception as e:
            row = {"task_id": task_id, "ok": False, "error": f"{type(e).__name__}: {e}"}
            print(f"  ERROR {row['error']}", flush=True)
            traceback.print_exc()
        rows.append(row)
        with summary_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")

    done = [r for r in rows if r.get("ok")]
    n_correct = sum(1 for r in rows if r.get("correct") is True)
    totals = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0,
              "reasoning_tokens": 0, "total_tokens": 0}
    for r in rows:
        for k in totals:
            totals[k] += int((r.get("usage") or {}).get(k) or 0)
    summary = {
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "setting": "slippage",
        "elapsed_s": round(time.perf_counter() - t0, 3),
        "n_tasks": len(rows),
        "n_ok": len(done),
        "n_error": sum(1 for r in rows if r.get("ok") is False),
        "n_skipped": sum(1 for r in rows if r.get("skipped")),
        "n_correct": n_correct,
        "total_usage": totals,
        "rows": rows,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(
        f"\n{len(done)}/{len(rows)} ok · correct {n_correct} · "
        f"{summary['elapsed_s'] / 60:.1f} min",
        flush=True,
    )


if __name__ == "__main__":
    main()
