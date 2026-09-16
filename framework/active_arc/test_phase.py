"""Answer each held-out item on its own branch of the exploration conversation.

Two things have to hold at once. The trial's reasoning -- built up across its
queries -- must still be in hand when the test is answered, or the active arm is
handicapped in a way the single-turn static arm is not. And no test item may be
visible while another is answered, or the per-item results are not independent
measurements.

Showing the items together satisfies the first and breaks the second. Branching
satisfies both: every item is asked on a fork taken at the end of exploration, so
each carries the whole history and none carries another item's grid or answer.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from framework.active_arc.headless_trial import (
    INVALID_INPUT_OR_RULE_MESSAGE,
    ActiveArcTrialSession,
    normalize_query_grid,
)
from framework.grids import Grid, clone_grid, is_equal_grid, validate_grid


def _answer_message(grid: Grid, index: int, n_items: int) -> str:
    lead = (
        "Testing stage. Apply the same transformation rule to test_input_grid and "
        "submit your predicted output grid with submit_final_answer "
        "(JSON array of rows; each cell an integer 0-9)."
    )
    if n_items > 1:
        lead += (
            f" This is test input {index + 1} of {n_items}; they are answered "
            "separately and you will not be told whether any is right."
        )
    return lead + "\n\n```json\n" + json.dumps({"test_input_grid": grid}) + "\n```"


def score_answer(session: ActiveArcTrialSession, index: int, grid: Any) -> Dict[str, Any]:
    """Score one submitted grid against the item at *index*."""
    items = session.test_items
    if index >= len(items):
        return {"ok": False, "error": "No such test item."}
    try:
        pred = normalize_query_grid(clone_grid(grid))
        validate_grid(pred)
    except (ValueError, TypeError):
        return {"ok": False, "error": INVALID_INPUT_OR_RULE_MESSAGE}
    gold = items[index][1]
    return {"ok": True, "correct": is_equal_grid(pred, gold), "recorded": True}


def test_item_prompt(session: ActiveArcTrialSession, index: int) -> str:
    items = session.test_items
    return _answer_message(clone_grid(items[index][0]), index, len(items))


def finalize(session: ActiveArcTrialSession, per_item: List[bool]) -> Dict[str, Any]:
    """Record per-item outcomes and close the trial, matching static's scoring."""
    session.test_item_correct = list(per_item)
    ok = bool(per_item) and all(per_item)
    session.test_correct = ok
    session.phase = "done"
    return {
        "ok": True,
        "correct": ok,
        "n_test_correct": sum(1 for v in per_item if v),
        "n_test_items": len(per_item),
        "query_count": session.query_count,
        "phase": session.phase,
        "done": True,
    }
