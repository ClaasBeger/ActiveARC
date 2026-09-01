"""Build JSON-serializable trial records from a session + agent loop result."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from framework.active_arc.headless_trial import ActiveArcTrialSession
from framework.grids import clone_grid


def _grid_pair_json(pair: Any) -> Dict[str, List[List[int]]]:
    return {
        "input": clone_grid(pair.input),
        "output": clone_grid(pair.output),
    }


def build_trial_record(
    session: ActiveArcTrialSession,
    result: Dict[str, Any],
    *,
    dataset: str,
    hot_start: bool,
    noisy_science: bool,
    re_trials: bool,
    fixed_test: bool,
) -> Dict[str, Any]:
    """Full trial artifact for saving / batch aggregation."""
    final = result.get("final") or {}
    correct = final.get("correct")
    if correct is None and isinstance(final.get("result"), dict):
        correct = final["result"].get("correct")

    return {
        "task_id": session.task_id,
        "seed": session.seed,
        "dataset": dataset,
        "backend": result.get("backend"),
        "model": result.get("model"),
        "reasoning_effort": result.get("reasoning_effort"),
        "flags": {
            "hot_start": hot_start,
            "noisy_science": noisy_science,
            "re_trials": re_trials,
            "fixed_test": fixed_test,
        },
        "trial": {
            "verifier_slot": session.verifier_slot,
            "hot_start_pair": session.hot_start_json(),
            "test_round": session.test_round,
            "test_input_query_count": session.test_input_query_count,
            "shown_test_rounds": len(session.shown_test_inputs),
            "test_input": (
                clone_grid(session.test_pair.input) if session.test_pair is not None else None
            ),
            "query_history": [
                {
                    "input": clone_grid(h["input"]),
                    "output": clone_grid(h["output"]),
                    "note": h.get("note"),
                    "queried_shown_test_input": h.get("queried_shown_test_input", False),
                    "matched_test_round": h.get("matched_test_round"),
                }
                for h in session.history
            ],
        },
        "final": final,
        "query_count": session.query_count,
        "test_input_query_count": session.test_input_query_count,
        "correct": correct,
        "phase": session.phase,
        "usage": result.get("usage"),
        "transcript": result.get("transcript"),
    }
