"""Predict one test output from a set of input-output pairs, in a fresh context.

Every arm of the matched-K comparison ends the same way: some number of pairs
have been assembled -- authored by the task designer, drawn at random from the
generator, or chosen by the model itself -- and a held-out input must be
answered from them. Sharing this module across the arms is what keeps the
comparison about the pairs rather than about how the question was phrased.

The context is rebuilt for every call, so predictions on different test items of
the same task cannot see each other, and none of them sees the exploration
transcript that produced the pairs.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Sequence

from framework.prompting.clients import (
    PROVIDER_OPENAI,
    ResponsesConversation,
    resolve_store,
    responses_extras,
)
from framework.prompting.response_logging import summarize_response, usage_totals

SUBMIT_PREDICTION_TOOL: Dict[str, Any] = {
    "type": "function",
    "name": "submit_prediction",
    "description": "Submit the predicted output grid for the test input.",
    "parameters": {
        "type": "object",
        "properties": {
            "grid": {
                "type": "array",
                "items": {"type": "array", "items": {"type": "integer"}},
            }
        },
        "required": ["grid"],
        "additionalProperties": False,
    },
    "strict": True,
}

PREDICTION_TOOLS: List[Dict[str, Any]] = [SUBMIT_PREDICTION_TOOL]


def _dumps(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"))


def pair_json(pair: Any) -> Dict[str, Any]:
    """Accept GridPair-likes and plain dicts alike."""
    if isinstance(pair, dict):
        return {"input": pair["input"], "output": pair["output"]}
    return {"input": pair.input, "output": pair.output}


def developer_prompt() -> str:
    return "\n".join([
        "You are solving a grid transformation task.",
        "Grids are rectangular matrices with integer colors 0-9.",
        "You are shown the task's training examples: input grids and the output grids they map to.",
        "Infer the transformation rule from those examples, apply it to the test input, and submit "
        "the resulting output grid with submit_prediction.",
        "Do not paste grids as plain text; the only way to answer is the submit_prediction call.",
    ])


def task_message(
    pairs: Sequence[Any],
    test_input: List[List[int]],
    test_index: int,
    n_tests: int,
) -> str:
    payload: Dict[str, Any] = {
        "train": [pair_json(p) for p in pairs],
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
    return (getattr(item, "call_id", None), getattr(item, "name", None),
            getattr(item, "arguments", None))


def _assistant_text(response: Any) -> Optional[str]:
    text = getattr(response, "output_text", None)
    if isinstance(text, str) and text.strip():
        return text
    parts: List[str] = []
    for item in getattr(response, "output", []) or []:
        if _output_item_type(item) != "message":
            continue
        content = item.get("content", []) if isinstance(item, dict) else getattr(item, "content", [])
        for block in content or []:
            txt = block.get("text") if isinstance(block, dict) else getattr(block, "text", None)
            if isinstance(txt, str) and txt.strip():
                parts.append(txt)
    return "\n".join(parts).strip() or None


def parse_prediction(arguments: Any) -> Dict[str, Any]:
    try:
        payload = json.loads(arguments) if isinstance(arguments, str) else (arguments or {})
    except (TypeError, ValueError):
        return {"ok": False, "error": "submit_prediction arguments were not valid JSON."}
    grid = payload.get("grid")
    if not isinstance(grid, list) or not grid:
        return {"ok": False, "error": "grid must be a non-empty list of rows."}
    rows: List[List[int]] = []
    width = None
    for row in grid:
        if not isinstance(row, list) or not row:
            return {"ok": False, "error": "every row must be a non-empty list of integers."}
        if width is None:
            width = len(row)
        elif len(row) != width:
            return {"ok": False, "error": "all rows must have the same length."}
        out_row: List[int] = []
        for cell in row:
            if not isinstance(cell, int) or isinstance(cell, bool) or not 0 <= cell <= 9:
                return {"ok": False, "error": "every cell must be an integer 0-9."}
            out_row.append(int(cell))
        rows.append(out_row)
    return {"ok": True, "grid": rows}


def predict_from_evidence(
    client: Any,
    pairs: Sequence[Any],
    test_input: List[List[int]],
    *,
    model: str,
    reasoning_effort: Optional[str],
    max_turns: int = 8,
    store: bool = True,
    provider: str = PROVIDER_OPENAI,
    test_index: int = 0,
    n_tests: int = 1,
) -> Dict[str, Any]:
    """One submit_prediction loop over *pairs*. Context is fresh for this call."""
    store = resolve_store(provider, store)
    convo = ResponsesConversation(provider, [
        {"role": "developer", "content": developer_prompt()},
        {"role": "user", "content": task_message(pairs, test_input, test_index, n_tests)},
    ])
    transcript: List[Dict[str, Any]] = []
    prediction: Optional[List[List[int]]] = None
    reason = "max_turns"

    for turn in range(max_turns):
        kwargs: Dict[str, Any] = {
            "model": model,
            "tools": PREDICTION_TOOLS,
            "store": store,
            **convo.create_kwargs(),
        }
        kwargs.update(responses_extras(provider, model, reasoning_effort))
        response = client.responses.create(**kwargs)
        calls = [it for it in (getattr(response, "output", None) or [])
                 if _output_item_type(it) == "function_call"]
        log = {
            "turn": turn,
            "response_id": response.id,
            "response": summarize_response(response),
            "assistant": _assistant_text(response),
            "tool_calls": [dict(zip(("call_id", "name", "arguments"), _function_call_fields(c)))
                           for c in calls],
            "tool_results": [],
        }
        transcript.append(log)
        convo.record_turn(response, [_function_call_fields(c) for c in calls],
                          assistant_text=_assistant_text(response))

        if not calls:
            reminder = ("No prediction was submitted. Call submit_prediction with "
                        '{"grid": [[...], ...]} for test_input.')
            log["tool_results"].append(
                {"name": "_protocol_reminder", "result": {"ok": False, "error": reminder}})
            convo.extend([{"role": "user", "content": reminder}])
            continue

        tool_outputs: List[Any] = []
        submitted = False
        for item in calls:
            call_id, name, arguments = _function_call_fields(item)
            if name != "submit_prediction":
                out = {"ok": False, "error": f"Unknown tool: {name}"}
            else:
                parsed = parse_prediction(arguments)
                if parsed.get("ok"):
                    prediction, out, submitted = parsed["grid"], {"ok": True, "recorded": True}, True
                else:
                    out = parsed
            log["tool_results"].append({"name": name, "result": out})
            tool_outputs.append({"type": "function_call_output", "call_id": call_id,
                                 "output": json.dumps(out)})
        convo.extend(tool_outputs)
        if submitted:
            reason = "submitted"
            break

    return {
        "prediction": prediction,
        "reason": reason,
        "transcript": transcript,
        "usage": usage_totals(transcript),
    }
