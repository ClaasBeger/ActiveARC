#!/usr/bin/env python3
"""Static evaluation: show the official train pairs, ask for the official test output.

No oracle, no queries, no generator -- the classical ARC protocol, for a
baseline next to active discovery and inverse query::

    python -m pipelines.run_static_batch --dataset arc --limit 400 \\
        --model gpt-5.6-luna --reasoning-effort low --out-dir experiments/runs/static_arc_agi_1_luna

One record per task. A task with several test inputs is asked one at a time,
each in a fresh context with the same train pairs; the task counts as correct
only if every test output is right (the usual ARC scoring). Writes
``manifest.json``, ``summary.jsonl`` and ``summary.json`` beside the records.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from framework.grids import is_equal_grid  # noqa: E402
from framework.inverse_query.prompts import _dumps  # noqa: E402
from framework.inverse_query.tools import STUDENT_TOOLS, parse_student_prediction  # noqa: E402
from framework.prompting.active_arc_tools import DEFAULT_OPENAI_MODEL  # noqa: E402
from framework.prompting.clients import (  # noqa: E402
    PROVIDER_OPENAI,
    PROVIDERS,
    ResponsesConversation,
    build_client,
    resolve_model,
    resolve_provider,
    resolve_store,
)
from framework.prompting.response_logging import summarize_response, usage_totals  # noqa: E402
from pipelines.run_active_arc_batch import _output_basename, _task_ids  # noqa: E402

NON_TRIAL_FILES = {"manifest.json", "summary.json", "summary.jsonl", "INVALID.json"}


def load_official(dataset: str, task_id: str):
    if dataset == "conceptarc":
        from framework.integrations.conceptarc_adapter import load_conceptarc_task
        return load_conceptarc_task(task_id)
    if dataset == "parc":
        from framework.tasks.parc_dataset import load_parc_task
        return load_parc_task(task_id)
    from framework.tasks.arc_dataset import load_task
    return load_task(task_id, load_alternative_verifiers=False)


def developer_prompt() -> str:
    return "\n".join([
        "You are solving a grid transformation task.",
        "Grids are rectangular matrices with integer colors 0-9.",
        "You are shown the task's training examples: input grids and the output grids they map to.",
        "Infer the transformation rule from those examples, apply it to the test input, and submit "
        "the resulting output grid with submit_prediction.",
        "Do not paste grids as plain text; the only way to answer is the submit_prediction call.",
    ])


def task_message(train_pairs, test_input, test_index: int, n_tests: int) -> str:
    payload: Dict[str, Any] = {
        "train": [{"input": p.input, "output": p.output} for p in train_pairs],
        "test_input": test_input,
    }
    if n_tests > 1:
        payload["test_item"] = test_index + 1
        payload["n_test_items"] = n_tests
    return ("Here is the task. Apply the rule shown by the training examples to test_input and "
            "submit the output grid with submit_prediction.\n\n```json\n%s\n```" % _dumps(payload))


def _output_item_type(item: Any) -> str:
    return str(getattr(item, "type", None) or (item.get("type") if isinstance(item, dict) else ""))


def _function_call_fields(item: Any):
    if isinstance(item, dict):
        return item.get("call_id"), item.get("name"), item.get("arguments")
    return getattr(item, "call_id", None), getattr(item, "name", None), getattr(item, "arguments", None)


def _assistant_text(response: Any) -> Optional[str]:
    parts: List[str] = []
    for item in getattr(response, "output", None) or []:
        if _output_item_type(item) != "message":
            continue
        for c in getattr(item, "content", None) or []:
            text = getattr(c, "text", None)
            if text:
                parts.append(text)
    return "\n".join(parts) if parts else None


def predict(client, train_pairs, test_input, *, test_index: int, n_tests: int, model: str,
            reasoning_effort: Optional[str], max_turns: int, store: bool,
            provider: str = PROVIDER_OPENAI) -> Dict[str, Any]:
    """One submit_prediction loop. Tool-less turns are nudged; the budget is the only stop."""
    transcript: List[Dict[str, Any]] = []
    convo = ResponsesConversation(provider, [
        {"role": "developer", "content": developer_prompt()},
        {"role": "user", "content": task_message(train_pairs, test_input, test_index, n_tests)},
    ])
    store = resolve_store(provider, store)
    prediction: Optional[List[List[int]]] = None
    reason = "max_turns"
    for turn in range(max_turns):
        kwargs: Dict[str, Any] = {"model": model, "tools": STUDENT_TOOLS, "store": store,
                                  **convo.create_kwargs()}
        if reasoning_effort is not None:
            kwargs["reasoning"] = {"effort": reasoning_effort}
        response = client.responses.create(**kwargs)
        calls = [it for it in (getattr(response, "output", None) or []) if _output_item_type(it) == "function_call"]
        log = {"turn": turn, "response_id": response.id, "response": summarize_response(response),
               "assistant": _assistant_text(response),
               "tool_calls": [dict(zip(("call_id", "name", "arguments"), _function_call_fields(c))) for c in calls],
               "tool_results": []}
        transcript.append(log)
        convo.record_turn(response, [_function_call_fields(c) for c in calls],
                          assistant_text=_assistant_text(response))
        if not calls:
            reminder = ("No prediction was submitted. Call submit_prediction with "
                        '{"grid": [[...], ...]} for test_input.')
            log["tool_results"].append({"name": "_protocol_reminder", "result": {"ok": False, "error": reminder}})
            convo.extend([{"role": "user", "content": reminder}])
            continue
        tool_outputs: List[Any] = []
        submitted = False
        for item in calls:
            call_id, name, arguments = _function_call_fields(item)
            if name != "submit_prediction":
                out = {"ok": False, "error": f"Unknown tool: {name}"}
            else:
                parsed = parse_student_prediction(arguments)
                if parsed.get("ok"):
                    prediction, out, submitted = parsed["grid"], {"ok": True, "recorded": True}, True
                else:
                    out = parsed
            log["tool_results"].append({"name": name, "result": out})
            tool_outputs.append({"type": "function_call_output", "call_id": call_id, "output": json.dumps(out)})
        convo.extend(tool_outputs)
        if submitted:
            reason = "submitted"
            break
    return {"prediction": prediction, "reason": reason, "transcript": transcript, "usage": usage_totals(transcript)}


def _generator_pairs(args, task_id: str, n: int):
    """n pairs drawn from the task's generator, in place of its authored ones.

    The random arm of the matched-K comparison: same count and same provenance
    as the pairs an active trial could have queried for, but chosen by nobody.
    Built from a trial session so the generator, verifier and seed are exactly
    the ones the active arm would have used on this task.
    """
    from framework.active_arc.headless_trial import create_trial_session
    from framework.active_arc.verifier_selection import sample_consistent_dynamic_pair
    from framework.grids import GridPair

    session = create_trial_session(seed=args.seed, task_id=task_id,
                                   hot_start=True, dataset=args.dataset)
    pairs = []
    exclude = []
    if session.hot_start_pair is not None:
        pairs.append(session.hot_start_pair)
        exclude.append(session.hot_start_pair.input)
    while len(pairs) < n:
        got = sample_consistent_dynamic_pair(
            session.task, session._verifier_fn(), session.rng,
            exclude_inputs=exclude or None,
        )
        if got is None:
            break
        pairs.append(GridPair(got.input, session._verifier_fn()(got.input)))
        exclude.append(got.input)
    return pairs


def run_one(client, args, task_id: str) -> Dict[str, Any]:
    task = load_official(args.dataset, task_id)
    tests = list(zip(task.test_inputs, task.test_outputs))
    train_pairs = task.train_pairs
    if args.pair_source == "generator":
        n = len(task.train_pairs) if args.n_pairs in (None, "auto") else int(args.n_pairs)
        train_pairs = _generator_pairs(args, task_id, n)
        if len(train_pairs) < n:
            return {"task_id": task_id, "error": "sampler_exhausted",
                    "n_pairs_wanted": n, "n_pairs_got": len(train_pairs)}
    items = []
    turns: List[Dict[str, Any]] = []
    for i, (tin, tout) in enumerate(tests):
        res = predict(client, train_pairs, tin, test_index=i, n_tests=len(tests), model=args.model,
                      reasoning_effort=args.reasoning_effort, max_turns=args.max_turns,
                      store=not args.no_store, provider=args.provider)
        pred = res["prediction"]
        items.append({"index": i, "input": tin, "gold_output": tout, "prediction": pred,
                      "correct": pred is not None and is_equal_grid(pred, tout), "reason": res["reason"],
                      "turns": len(res["transcript"]), "usage": res["usage"]})
        turns.extend(res["transcript"])
    return {
        "setting": "static",
        "task_id": task_id, "dataset": args.dataset, "backend": "responses",
        "model": args.model, "reasoning_effort": args.reasoning_effort,
        "n_train": len(task.train_pairs), "n_test": len(tests),
        "n_test_correct": sum(1 for it in items if it["correct"]),
        "correct": bool(items) and all(it["correct"] for it in items),
        "test_items": items,
        "usage": usage_totals(turns),
        "transcript": turns,
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Static (train pairs -> test output) evaluation")
    p.add_argument("--dataset", choices=["arc", "arc2", "conceptarc", "parc"], default="arc")
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--per-concept-limit", type=int, default=None)
    p.add_argument("--task-id", action="append", dest="task_ids", default=None)
    p.add_argument("--out-dir", type=str, required=True)
    p.add_argument("--model", type=str, default=None)
    p.add_argument("--provider", choices=list(PROVIDERS), default=None,
                   help="Default: inferred from --model, else openai.")
    p.add_argument("--pair-source", choices=["official", "generator"], default="official",
                   help="'generator' replaces the authored training pairs with the same "
                        "number drawn at random from the task's generator -- the random "
                        "arm of the matched-K comparison.")
    p.add_argument("--n-pairs", type=str, default="auto",
                   help="With --pair-source generator: how many pairs to draw "
                        "(default 'auto' = the task's own training-pair count).")
    p.add_argument("--seed", type=int, default=0,
                   help="Seed for generator pair sampling.")
    p.add_argument("--reasoning-effort", type=str, default="low")
    p.add_argument("--max-turns", type=int, default=8)
    p.add_argument("--no-store", action="store_true")
    p.add_argument("--skip-existing", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--dry-run", action="store_true", help="Print the selected task ids and exit.")
    args = p.parse_args()
    args.model = args.model or os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    if args.reasoning_effort and args.reasoning_effort.lower() == "none":
        args.reasoning_effort = None

    task_ids = _task_ids(SimpleNamespace(dataset=args.dataset, offset=args.offset, limit=args.limit,
                                         per_concept_limit=args.per_concept_limit, task_ids=args.task_ids))
    if not task_ids:
        raise SystemExit("No task ids selected.")
    if args.dry_run:
        print(json.dumps({"dataset": args.dataset, "n": len(task_ids), "task_ids": task_ids}, indent=1))
        return

    args.provider = resolve_provider(args.provider, args.model)
    args.model = resolve_model(args.provider, args.model)
    client = build_client(args.provider)

    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"started_at": datetime.now(timezone.utc).isoformat(), "setting": "static", "dataset": args.dataset,
                "model": args.model, "provider": args.provider,
                "pair_source": args.pair_source, "n_pairs": args.n_pairs, "seed": args.seed,
                "reasoning_effort": args.reasoning_effort, "max_turns": args.max_turns,
                "offset": args.offset, "limit": args.limit, "per_concept_limit": args.per_concept_limit,
                "task_ids": task_ids}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    summary_path = out_dir / "summary.jsonl"
    rows: List[Dict[str, Any]] = []
    t0 = time.perf_counter()
    for i, task_id in enumerate(task_ids, start=1):
        out_path = out_dir / f"{_output_basename(task_id)}.json"
        if args.skip_existing and out_path.is_file():
            rec = json.loads(out_path.read_text(encoding="utf-8"))
            row = {"task_id": task_id, "skipped": True, "correct": rec.get("correct"), "n_test": rec.get("n_test"),
                   "n_test_correct": rec.get("n_test_correct"), "usage": rec.get("usage")}
            rows.append(row); summary_path.open("a", encoding="utf-8").write(json.dumps(row) + "\n")
            print(f"[{i}/{len(task_ids)}] skip existing {task_id}", flush=True)
            continue
        started = time.perf_counter()
        try:
            rec = run_one(client, args, task_id)
            rec["elapsed_s"] = round(time.perf_counter() - started, 3)
            out_path.write_text(json.dumps(rec, indent=2), encoding="utf-8")
            row = {"task_id": task_id, "ok": True, "correct": rec["correct"], "n_test": rec["n_test"],
                   "n_test_correct": rec["n_test_correct"], "usage": rec["usage"], "elapsed_s": rec["elapsed_s"],
                   "reasons": [it["reason"] for it in rec["test_items"]]}
            status = "ok"
        except Exception as e:
            rec = {"task_id": task_id, "error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc(),
                   "elapsed_s": round(time.perf_counter() - started, 3)}
            out_path.write_text(json.dumps(rec, indent=2), encoding="utf-8")
            row = {"task_id": task_id, "ok": False, "error": rec["error"], "elapsed_s": rec["elapsed_s"]}
            status = "ERROR"
        rows.append(row); summary_path.open("a", encoding="utf-8").write(json.dumps(row) + "\n")
        extra = f" correct={row.get('correct')} tests={row.get('n_test_correct')}/{row.get('n_test')}" if row.get("ok") else f" {row.get('error')}"
        print(f"[{i}/{len(task_ids)}] {status} {task_id}{extra}", flush=True)

    scored = [r for r in rows if r.get("correct") is not None]
    summary = {"finished_at": datetime.now(timezone.utc).isoformat(), "elapsed_s": round(time.perf_counter() - t0, 3),
               "n_tasks": len(task_ids), "n_ok": sum(1 for r in rows if r.get("ok")), "n_error": sum(1 for r in rows if r.get("ok") is False),
               "n_skipped": sum(1 for r in rows if r.get("skipped")), "n_correct": sum(1 for r in scored if r["correct"]),
               "accuracy": (sum(1 for r in scored if r["correct"]) / len(scored)) if scored else None,
               "total_usage": {k: sum((r.get("usage") or {}).get(k, 0) for r in rows if isinstance(r.get("usage"), dict))
                               for k in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_tokens", "total_tokens")},
               "rows": rows}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2), flush=True)


if __name__ == "__main__":
    main()
