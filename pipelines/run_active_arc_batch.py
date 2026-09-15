#!/usr/bin/env python3
"""Run the ActiveARC OpenAI agent on many ARC tasks sequentially.

Example::

    python -m pipelines.run_active_arc_batch --limit 100 --seed 0 \\
        --out-dir experiments/runs/batch100_seed0

    python -m pipelines.run_active_arc_batch --dataset arc2 --limit 200 --seed 0 \\
        --out-dir experiments/runs/arc_agi_2_seed0

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
from typing import Optional

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from framework.active_arc.headless_trial import create_trial_session
from framework.active_arc.trial_record import build_trial_record
from framework.prompting.active_arc_openai import run_openai_agent_loop
from framework.prompting.active_arc_responses import run_active_arc_responses_loop
from framework.prompting.active_arc_tools import DEFAULT_OPENAI_MODEL  # noqa: F401
from framework.active_arc.evidence_test import run_evidence_tests
from framework.prompting.clients import PROVIDERS, build_client, resolve_target
from framework.tasks.arc_dataset import list_arc_agi_1_task_ids


def _output_basename(task_id: str) -> str:
    """Filesystem-safe name (ConceptARC ids contain ``/``)."""
    return task_id.replace("/", "__")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Batch ActiveARC agent runs")
    p.add_argument(
        "--dataset",
        choices=["arc", "arc2", "conceptarc", "parc"],
        default="arc",
        help="Task pool: arc (ARC-AGI-1 training, 400 ids), arc2 (validated ARC-AGI-2), "
        "conceptarc, or parc (P-ARC).",
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
    p.add_argument(
        "--provider",
        choices=list(PROVIDERS),
        default=None,
        help="Model provider. Default: inferred from --model (a 'vendor/model' id "
        "means openrouter), else ACTIVEARC_PROVIDER, else openai. OpenRouter has "
        "no Responses API, so it forces --backend chat.",
    )
    p.add_argument("--model", type=str, default=None)
    p.add_argument(
        "--forced-k",
        type=str,
        default=None,
        metavar="auto|N",
        help="Require exactly this many successful queries before testing, so the "
        "trial's evidence count matches the other arms. 'auto' uses the task's own "
        "training-pair count minus the hot start. Omitted = the model stops when it "
        "likes (free interaction).",
    )
    p.add_argument(
        "--test-source",
        choices=["sampled", "official", "both"],
        default="sampled",
        help="Which held-out item(s) the test phase asks about, answered in the "
        "exploration conversation so the reasoning built up across queries is kept: "
        "the trial's generator-sampled pair (default), the task's own authored "
        "item(s) -- what the static arm is scored on -- or both, shown together.",
    )
    p.add_argument(
        "--evidence-test",
        choices=["none", "official", "sampled", "both"],
        default="none",
        help="Optional diagnostic, off by default. Re-answers held-out items from the "
        "gathered pairs alone in a fresh context, discarding the exploration "
        "reasoning -- a reset-copy reading of whether the evidence carries the rule. "
        "Not the trial's score; use --test-source for that.",
    )
    p.add_argument("--evidence-max-turns", type=int, default=8)
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
    p.add_argument("--re-trials", action=argparse.BooleanOptionalAction, default=False)
    p.add_argument(
        "--wrong-answer-penalty",
        type=int,
        default=0,
        metavar="N",
        help="Announce and apply +N to query count on a wrong test answer "
        "(0 = do not announce). Trial still ends unless --re-trials.",
    )
    p.add_argument(
        "--fixed-test",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Keep one test sample for the whole trial (default: resample on each request_test).",
    )
    p.add_argument("--noise-probability", type=float, default=0.12)
    p.add_argument(
        "--program-test",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Test stage asks for a Python program (scored on train/test/generator "
        "stable+dynamic) instead of a single output grid.",
    )
    p.add_argument(
        "--defer-program-eval",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="With --program-test: record the submitted program without scoring it "
        "(score later with `python -m pipelines.score_programs <run-dir>`).",
    )
    p.add_argument(
        "--skip-existing",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Skip tasks whose per-task JSON already exists (default: true).",
    )
    p.add_argument(
        "--task-id",
        type=str,
        action="append",
        default=None,
        dest="task_ids",
        help="Run only these task ids (repeatable). Overrides --offset/--limit, "
        "which is what you want when redoing a handful of trials in place.",
    )
    return p.parse_args()


def _conceptarc_sort_key(task_id: str) -> tuple[str, int, str]:
    concept, name = task_id.split("/", 1)
    digits = "".join(ch for ch in name if ch.isdigit())
    return (concept, int(digits) if digits else 0, name)



_NON_TRIAL_FILES = {
    "manifest.json", "summary.json", "summary.jsonl", "program_scores.json",
    "oracle_recheck.json", "oracle_recheck_canon.json", "INVALID.json",
}


def _row_from_record(task_id: str, record: dict) -> dict:
    """The summary row for one trial, from its record (fresh or read back from disk)."""
    if record.get("error") and "transcript" not in record:
        return {"task_id": task_id, "ok": False, "error": record["error"],
                "elapsed_s": record.get("elapsed_s")}
    return {
        "task_id": task_id,
        "ok": True,
        "correct": record.get("correct"),
        "query_count": record.get("query_count"),
        "test_input_query_count": record.get("test_input_query_count", 0),
        "turns": len(record.get("transcript") or []),
        "usage": record.get("usage"),
        "elapsed_s": record.get("elapsed_s"),
        "final_reason": (record.get("final") or {}).get("reason"),
    }


def _task_ids(args: argparse.Namespace) -> list[str]:
    if args.task_ids:
        return list(args.task_ids)
    if args.dataset == "arc":
        ids = list_arc_agi_1_task_ids()
        if not ids:
            raise SystemExit("No ARC-AGI-1 training tasks found.")
        return ids[args.offset : args.offset + args.limit]

    if args.dataset == "arc2":
        from framework.integrations.agi2_verifiers import list_agi2_valid_task_ids

        ids = list_agi2_valid_task_ids()
        if not ids:
            raise SystemExit("No validated ARC-AGI-2 verifiers under external/agi2_verifiers/valid.")
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


def _forced_k_for(args: argparse.Namespace, task_id: str) -> Optional[int]:
    """How many queries this trial must make, to match the evidence the other arms get.

    "auto" reads the task's own training-pair count, so the trial ends holding as
    many pairs as the static arm is shown: the hot start counts as one of them,
    hence K-1 queries. Tasks differ (2 to 10 pairs, median 3), so the budget is
    per task rather than a single global number.
    """
    if args.forced_k is None:
        return None
    if str(args.forced_k).lower() == "auto":
        from pipelines.run_static_batch import load_official
        n_pairs = len(load_official(args.dataset, task_id).train_pairs)
        k = n_pairs - (1 if args.hot_start else 0)
    else:
        k = int(args.forced_k)
    return max(0, k)


def _run_one(args: argparse.Namespace, task_id: str) -> dict:
    forced = _forced_k_for(args, task_id)
    session = create_trial_session(
        seed=args.seed,
        task_id=task_id,
        forced_queries=forced,
        test_source=args.test_source,
        hot_start=args.hot_start,
        noisy_science=args.noisy_science,
        re_trials=args.re_trials,
        wrong_answer_penalty=args.wrong_answer_penalty,
        noise_probability=args.noise_probability,
        dataset=args.dataset,
        fixed_test=args.fixed_test,
        program_test=args.program_test,
        defer_program_eval=args.defer_program_eval,
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
    if args.evidence_test != "none" and not args.program_test:
        try:
            result["evidence_test"] = run_evidence_tests(
                build_client(args.provider),
                session,
                model=args.model,
                reasoning_effort=reasoning_effort,
                which=args.evidence_test,
                max_turns=args.evidence_max_turns,
                provider=args.provider,
            )
        except Exception as e:
            result["evidence_test"] = {"error": f"{type(e).__name__}: {e}"}

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

    # Resolve once so every trial, and the manifest, record what actually ran.
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
        "dataset": args.dataset,
        "backend": args.backend,
        "provider": args.provider,
        "model": args.model,
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
            "wrong_answer_penalty": args.wrong_answer_penalty,
            "program_test": args.program_test,
            "defer_program_eval": args.defer_program_eval,
        },
    }
    manifest_path = out_dir / "manifest.json"
    if args.task_ids and manifest_path.is_file():
        # Re-recording a few trials into an existing run: the run's manifest
        # stays the run's, and the re-recording is logged on it instead.
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        existing.setdefault("rerecordings", []).append({
            "at": manifest["started_at"], "task_ids": task_ids,
            "model": manifest["model"], "reasoning_effort": manifest["reasoning_effort"],
            "flags": manifest["flags"],
        })
        manifest = existing
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

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
            row = _row_from_record(task_id, record)
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

    if args.task_ids:
        # The summary describes the whole run directory. Rows for trials not
        # touched by this invocation come from their files on disk.
        touched = {r["task_id"] for r in rows}
        for f in sorted(out_dir.glob("*.json")):
            if f.name in _NON_TRIAL_FILES:
                continue
            try:
                rec = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            tid = rec.get("task_id")
            if not tid or tid in touched:
                continue
            rows.append(_row_from_record(tid, rec))
        rows.sort(key=lambda r: str(r.get("task_id")))
        task_ids = [r["task_id"] for r in rows]

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
        # Billed cost, present only for providers that report it (OpenRouter).
        "total_cost": round(
            sum(
                (r.get("usage") or {}).get("cost", 0.0)
                for r in rows
                if isinstance(r.get("usage"), dict)
            ),
            6,
        ),
        "rows": rows,
    }
    (out_dir / "summary.json").write_text(json.dumps(finished, indent=2), encoding="utf-8")
    print(json.dumps({k: finished[k] for k in finished if k != "rows"}, indent=2), flush=True)


if __name__ == "__main__":
    main()
