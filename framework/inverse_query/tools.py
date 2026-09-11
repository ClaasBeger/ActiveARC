"""Teacher and student tool schemas for Inverse Query Generation."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from framework.inverse_query.session import InverseQuerySession

_GRID_SCHEMA: Dict[str, Any] = {
    "type": "array",
    "description": "Rectangular matrix; each cell is an integer color 0–9.",
    "items": {
        "type": "array",
        "items": {"type": "integer", "minimum": 0, "maximum": 9},
    },
}

SHOW_EXAMPLE_TOOL: Dict[str, Any] = {
    "type": "function",
    "name": "show_example",
    "description": (
        "Show the Student a labeled input-output pair that you authored. "
        "If your output matches the rule, the pair is shown and you receive a success "
        "acknowledgement only. If it does not match, the pair is not shown and you "
        "receive the gold output so you can correct it."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "input_grid": _GRID_SCHEMA,
            "output_grid": _GRID_SCHEMA,
        },
        "required": ["input_grid", "output_grid"],
        "additionalProperties": False,
    },
    "strict": True,
}

SHOW_TRANSFORMED_INPUT_TOOL: Dict[str, Any] = {
    "type": "function",
    "name": "show_transformed_input",
    "description": (
        "Provide only an input grid. The environment applies the verifier and shows "
        "the resulting gold input-output pair to the student."
    ),
    "parameters": {
        "type": "object",
        "properties": {"input_grid": _GRID_SCHEMA},
        "required": ["input_grid"],
        "additionalProperties": False,
    },
    "strict": True,
}

QUERY_STUDENT_TOOL: Dict[str, Any] = {
    "type": "function",
    "name": "query_student",
    "description": (
        "Probe the student with an input of your choice. You receive the student's "
        "predicted output, the gold output, and whether they matched. The student does "
        "not see the gold pair unless you later show it with show_example or "
        "show_transformed_input."
    ),
    "parameters": {
        "type": "object",
        "properties": {"input_grid": _GRID_SCHEMA},
        "required": ["input_grid"],
        "additionalProperties": False,
    },
    "strict": True,
}

START_EXAM_TOOL: Dict[str, Any] = {
    "type": "function",
    "name": "start_exam",
    "description": (
        "End teaching and send the student to the exam: they must solve held-out "
        "generator inputs (unseen in demonstrations or probes) with the history so far. "
        "No further teaching after this."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
    "strict": True,
}

SUBMIT_PREDICTION_TOOL: Dict[str, Any] = {
    "type": "function",
    "name": "submit_prediction",
    "description": (
        "Submit your predicted output grid for the current input. "
        "Same shape as the input is not required; each cell an integer 0–9."
    ),
    "parameters": {
        "type": "object",
        "properties": {"grid": _GRID_SCHEMA},
        "required": ["grid"],
        "additionalProperties": False,
    },
    "strict": True,
}

TEACHER_TOOLS: List[Dict[str, Any]] = [
    SHOW_EXAMPLE_TOOL,
    SHOW_TRANSFORMED_INPUT_TOOL,
    QUERY_STUDENT_TOOL,
    START_EXAM_TOOL,
]
STUDENT_TOOLS: List[Dict[str, Any]] = [SUBMIT_PREDICTION_TOOL]


def execute_teacher_tool(
    session: InverseQuerySession,
    name: str,
    arguments: Optional[str],
) -> Dict[str, Any]:
    args: Dict[str, Any] = {}
    if arguments:
        try:
            args = json.loads(arguments)
        except json.JSONDecodeError as e:
            return {"ok": False, "error": f"Invalid JSON arguments: {e}"}

    if name == "show_example":
        return session.show_example(args.get("input_grid"), args.get("output_grid"))
    if name == "show_transformed_input":
        return session.show_transformed_input(args.get("input_grid"))
    if name == "query_student":
        prepared = session.prepare_probe(args.get("input_grid"))
        if not prepared.get("ok"):
            return prepared
        return {
            "ok": True,
            "delegate": "query_student",
            "input": prepared["input"],
            "gold": prepared["gold"],
        }
    if name == "start_exam":
        return session.start_exam()
    return {"ok": False, "error": f"Unknown tool: {name}"}


def parse_student_prediction(arguments: Optional[str]) -> Dict[str, Any]:
    args: Dict[str, Any] = {}
    if arguments:
        try:
            args = json.loads(arguments)
        except json.JSONDecodeError as e:
            return {"ok": False, "error": f"Invalid JSON arguments: {e}"}
    grid = args.get("grid")
    if not isinstance(grid, list):
        return {"ok": False, "error": "Missing or invalid grid for submit_prediction."}
    return {"ok": True, "grid": grid}
