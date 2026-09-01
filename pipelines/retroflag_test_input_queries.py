#!/usr/bin/env python3
"""Retroactively flag submit_query calls that reuse a previously shown test input."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from framework.grids import Grid, clone_grid, is_equal_grid


def audit_duplicate_shown_tests(trial: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return duplicate shown test-input events from a trial transcript."""
    shown: List[Grid] = []
    dups: List[Dict[str, Any]] = []
    for turn in trial.get("transcript") or []:
        calls = turn.get("tool_calls") or []
        results = turn.get("tool_results") or []
        for i, call in enumerate(calls):
            if call.get("name") != "finish_exploration":
                continue
            if i >= len(results):
                continue
            res = results[i].get("result") or {}
            grid = res.get("test_input_grid")
            if not grid:
                continue
            rnd = int(res.get("test_round") or len(shown) + 1)
            for j, prev in enumerate(shown, start=1):
                if is_equal_grid(grid, prev):
                    dups.append(
                        {
                            "test_round": rnd,
                            "duplicate_of_round": j,
                            "turn": turn.get("turn"),
                        }
                    )
                    break
            shown.append(clone_grid(grid))
    return dups


def _audit_duplicate_shown_tests(run_dir: Path) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for path in sorted(run_dir.glob("*.json")):
        if path.name in ("manifest.json", "summary.json"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if "transcript" not in data:
            continue
        dups = audit_duplicate_shown_tests(data)
        if dups:
            out.append({"task_id": data.get("task_id", path.stem), "duplicates": dups})
    return out


def _parse_args(raw: str) -> Dict[str, Any]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def retroflag_trial(trial: Dict[str, Any]) -> Dict[str, Any]:
    """Annotate transcript + trial metadata with test-input-query flags."""
    shown: List[Tuple[int, Grid]] = []
    query_history: List[Dict[str, Any]] = []
    test_input_query_count = 0

    for turn in trial.get("transcript") or []:
        calls = turn.get("tool_calls") or []
        results = turn.get("tool_results") or []
        for i, call in enumerate(calls):
            name = call.get("name")
            args = _parse_args(call.get("arguments") or "{}")
            result: Dict[str, Any] = {}
            if i < len(results):
                result = dict(results[i].get("result") or {})

            if name == "finish_exploration" and result.get("test_input_grid"):
                rnd = int(result.get("test_round") or len(shown) + 1)
                shown.append((rnd, clone_grid(result["test_input_grid"])))

            if name == "submit_query" and isinstance(args.get("grid"), list):
                inp = args["grid"]
                matched_round: Optional[int] = None
                for rnd, test_in in shown:
                    if is_equal_grid(inp, test_in):
                        matched_round = rnd
                        break
                if matched_round is not None:
                    test_input_query_count += 1
                    result["queried_shown_test_input"] = True
                    result["matched_test_round"] = matched_round
                elif result.get("ok"):
                    result.pop("queried_shown_test_input", None)
                    result.pop("matched_test_round", None)

                if i < len(results):
                    results[i]["result"] = result

                if result.get("ok") and result.get("output_grid") is not None:
                    query_history.append(
                        {
                            "input": clone_grid(inp),
                            "output": clone_grid(result["output_grid"]),
                            "note": result.get("note"),
                            "queried_shown_test_input": matched_round is not None,
                            "matched_test_round": matched_round,
                        }
                    )

    trial["test_input_query_count"] = test_input_query_count
    trial_ctx = trial.setdefault("trial", {})
    trial_ctx["test_input_query_count"] = test_input_query_count
    trial_ctx["shown_test_rounds"] = len(shown)
    trial_ctx["query_history"] = query_history
    return trial


def retroflag_run_dir(run_dir: Path) -> Dict[str, Any]:
    """Update all per-task JSON files and refresh summary.json / summary.jsonl."""
    rows: List[Dict[str, Any]] = []
    n_tricks = 0
    n_tasks_with_trick = 0

    for path in sorted(run_dir.glob("*.json")):
        if path.name in ("manifest.json", "summary.json"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if "transcript" not in data:
            continue
        retroflag_trial(data)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        count = int(data.get("test_input_query_count") or 0)
        if count:
            n_tricks += count
            n_tasks_with_trick += 1
        rows.append(
            {
                "task_id": data.get("task_id", path.stem),
                "ok": "error" not in data,
                "correct": data.get("correct"),
                "query_count": data.get("query_count"),
                "test_input_query_count": count,
                "turns": len(data.get("transcript") or []),
                "usage": data.get("usage"),
                "elapsed_s": data.get("elapsed_s"),
                "final_reason": (data.get("final") or {}).get("reason"),
            }
        )

    summary_path = run_dir / "summary.json"
    if summary_path.is_file():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    else:
        summary = {}
    summary["rows"] = rows
    summary["test_input_query_total"] = n_tricks
    summary["n_tasks_with_test_input_query"] = n_tasks_with_trick
    dup_rows = _audit_duplicate_shown_tests(run_dir)
    summary["duplicate_shown_test_input_tasks"] = dup_rows
    summary["n_tasks_with_duplicate_shown_test"] = len(dup_rows)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    jsonl_path = run_dir / "summary.jsonl"
    jsonl_path.write_text(
        "\n".join(json.dumps(r) for r in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )
    return {
        "n_tasks": len(rows),
        "test_input_query_total": n_tricks,
        "n_tasks_with_test_input_query": n_tasks_with_trick,
        "n_tasks_with_duplicate_shown_test": len(dup_rows),
        "duplicate_shown_test_input_tasks": dup_rows,
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Retroflag test-input queries in trial JSONs")
    p.add_argument("run_dir", type=Path, help="Directory with per-task trial JSON files")
    args = p.parse_args()
    stats = retroflag_run_dir(args.run_dir)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
