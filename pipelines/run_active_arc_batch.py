#!/usr/bin/env python3
"""Run the ActiveARC OpenAI agent on many ARC tasks sequentially.

Example::

    python -m pipelines.run_active_arc_batch --limit 100 --seed 0 \\
        --out-dir experiments/runs/batch100_seed0

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

from framework.active_arc.headless_trial import create_trial_session
from framework.active_arc.trial_record import build_trial_record
from framework.prompting.active_arc_openai import run_openai_agent_loop
from framework.prompting.active_arc_responses import run_active_arc_responses_loop
from framework.prompting.active_arc_tools import DEFAULT_OPENAI_MODEL
from framework.tasks.arc_dataset import ARC_ORIGINAL_DIR


def _output_basename(task_id: str) -> str:
    """Filesystem-safe name (ConceptARC ids contain ``/``)."""
    return task_id.replace("/", "__")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Batch ActiveARC agent runs")
    p.add_argument(
        "--dataset",
        choices=["arc", "conceptarc", "parc"],
        default="arc",
        help="Task pool: arc (default), conceptarc, or parc (P-ARC).",
    )
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument(
        "--per-concept-limit",
        type=int,
        default=None,
        help="ConceptARC only: max exported programs per concept (e.g. 10 for originals 1–10).",
    )
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out-dir", type=str, required=True)
    p.add_argument("--backend", choices=["responses", "chat"], default="responses")
    p.add_argument("--model", type=str, default=None)
    p.add_argument("--max-turns", type=int, default=64)
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument(
        "--reasoning-effort",
        type=str,
        default="low",
        help="Responses backend only; pass 'none' to omit.",
    )
    p.add_argument("--hot-start", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--noisy-science", action="store_true")
    p.add_argument("--re-trials", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument(
        "--fixed-test",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Keep one test sample for the whole trial (default: resample on each finish_exploration).",
    )
    p.add_argument("--noise-probability", type=float, default=0.12)
    p.add_argument(
        "--skip-existing",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Skip tasks whose per-task JSON already exists (default: true).",
    )
    return p.parse_args()


def _conceptarc_sort_key(task_id: str) -> tuple[str, int, str]:
    concept, name = task_id.split("/", 1)
    digits = "".join(ch for ch in name if ch.isdigit())
    return (concept, int(digits) if digits else 0, name)


def _task_ids(args: argparse.Namespace) -> list[str]:
    if args.dataset == "arc":
        ids = sorted(p.stem for p in ARC_ORIGINAL_DIR.glob("*.json"))
        return ids[args.offset : args.offset + args.limit]

    if args.dataset == "conceptarc":
        from framework.integrations.conceptarc_adapter import (
            conceptarc_available,
            list_conceptarc_concepts,
            list_conceptarc_task_ids,
        )

        if not conceptarc_available():
            raise SystemExit("ConceptARC programs not available.")
        all_ids = list(list_conceptarc_task_ids())
        if args.per_concept_limit is not None:
            picked: list[str] = []
            for concept in list_conceptarc_concepts():
                concept_ids = sorted(
                    (i for i in all_ids if i.split("/", 1)[0] == concept),
                    key=_conceptarc_sort_key,
                )
                picked.extend(concept_ids[: args.per_concept_limit])
            all_ids = sorted(picked, key=_conceptarc_sort_key)
        return all_ids[args.offset : args.offset + args.limit]

    if args.dataset == "parc":
        from framework.tasks.parc_dataset import list_parc_task_ids, parc_available

        if not parc_available():
            raise SystemExit("P-ARC Test2 data not available.")
        ids = list(list_parc_task_ids())
        return ids[args.offset : args.offset + args.limit]

    raise SystemExit(f"Unsupported dataset: {args.dataset}")


def _run_one(args: argparse.Namespace, task_id: str) -> dict:
    session = create_trial_session(
        seed=args.seed,
        task_id=task_id,
        hot_start=args.hot_start,
        noisy_science=args.noisy_science,
        re_trials=args.re_trials,
        noise_probability=args.noise_probability,
        dataset=args.dataset,
        fixed_test=args.fixed_test,
    )
    reasoning_effort = None if args.reasoning_effort.lower() == "none" else args.reasoning_effort
    if args.backend == "responses":
        result = run_active_arc_responses_loop(
            session,
            model=args.model,
            max_turns=args.max_turns,
            reasoning_effort=reasoning_effort,
        )
    else:
        result = run_openai_agent_loop(
            session,
            model=args.model,
            max_turns=args.max_turns,
            temperature=args.temperature,
        )
    return build_trial_record(
        session,
        result,
        dataset=args.dataset,
        hot_start=args.hot_start,
        noisy_science=args.noisy_science,
        re_trials=args.re_trials,
        fixed_test=args.fixed_test,
    )


def main() -> None:
    args = _parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    task_ids = _task_ids(args)
    if not task_ids:
        raise SystemExit("No task ids selected.")

    manifest = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "dataset": args.dataset,
        "backend": args.backend,
        "model": args.model or DEFAULT_OPENAI_MODEL,
        "reasoning_effort": args.reasoning_effort,
        "seed": args.seed,
        "offset": args.offset,
        "limit": args.limit,
        "per_concept_limit": args.per_concept_limit,
        "task_ids": task_ids,
        "flags": {
            "hot_start": args.hot_start,
            "noisy_science": args.noisy_science,
            "re_trials": args.re_trials,
            "fixed_test": args.fixed_test,
        },
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
                    "correct": existing.get("correct"),
                    "query_count": existing.get("query_count"),
                    "usage": existing.get("usage"),
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
                "correct": record.get("correct"),
                "query_count": record.get("query_count"),
                "test_input_query_count": record.get("test_input_query_count", 0),
                "turns": len(record.get("transcript") or []),
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
            status = "ERR"
            print(f"  {status} {task_id}: {err}", flush=True)

        rows.append(row)
        with summary_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        if status == "ok":
            print(
                f"  ok correct={row.get('correct')} queries={row.get('query_count')} "
                f"test_input_queries={row.get('test_input_query_count', 0)} "
                f"turns={row.get('turns')} tokens={row.get('usage', {}).get('total_tokens')}",
                flush=True,
            )

    finished = {
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_s": round(time.perf_counter() - t0, 3),
        "n_tasks": len(task_ids),
        "n_ok": sum(1 for r in rows if r.get("ok") is True),
        "n_error": sum(1 for r in rows if r.get("ok") is False),
        "n_skipped": sum(1 for r in rows if r.get("skipped")),
        "n_correct": sum(1 for r in rows if r.get("correct") is True),
        "n_sampler_exhausted": sum(
            1 for r in rows if r.get("final_reason") == "sampler_exhausted"
        ),
        "total_usage": {
            k: sum((r.get("usage") or {}).get(k, 0) for r in rows if isinstance(r.get("usage"), dict))
            for k in (
                "input_tokens",
                "cached_input_tokens",
                "output_tokens",
                "reasoning_tokens",
                "total_tokens",
            )
        },
        "rows": rows,
    }
    (out_dir / "summary.json").write_text(json.dumps(finished, indent=2), encoding="utf-8")
    print(json.dumps({k: finished[k] for k in finished if k != "rows"}, indent=2), flush=True)


if __name__ == "__main__":
    main()
