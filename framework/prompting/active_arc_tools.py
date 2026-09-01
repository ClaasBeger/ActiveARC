"""Shared ActiveARC tool schemas, prompts, and environment dispatch for API agents."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from framework.active_arc.headless_trial import ActiveArcTrialSession
from framework.grids import clone_grid

DEFAULT_OPENAI_MODEL = "gpt-5.6-luna"

_GRID_SCHEMA: Dict[str, Any] = {
    "type": "array",
    "description": "Rectangular matrix; each cell is an integer color 0–9.",
    "items": {
        "type": "array",
        "items": {"type": "integer", "minimum": 0, "maximum": 9},
    },
}

_SUBMIT_QUERY_TOOL: Dict[str, Any] = {
    "type": "function",
    "name": "submit_query",
    "description": (
        "Exploration stage only. Submit an input grid; the environment returns the transformed output grid. "
        "Each successful call increases your query count by 1."
    ),
    "parameters": {
        "type": "object",
        "properties": {"grid": _GRID_SCHEMA},
        "required": ["grid"],
        "additionalProperties": False,
    },
    "strict": True,
}

_FINISH_EXPLORATION_TOOL: Dict[str, Any] = {
    "type": "function",
    "name": "finish_exploration",
    "description": (
        "Exploration stage only. Enter the testing stage and receive a held-out test input grid."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
    "strict": True,
}

_SUBMIT_FINAL_ANSWER_TOOL: Dict[str, Any] = {
    "type": "function",
    "name": "submit_final_answer",
    "description": (
        "Testing stage only. Submit your predicted output grid for the test input. "
        "Same shape as test_input_grid; each cell an integer 0–9."
    ),
    "parameters": {
        "type": "object",
        "properties": {"grid": _GRID_SCHEMA},
        "required": ["grid"],
        "additionalProperties": False,
    },
    "strict": True,
}

RESPONSES_EXPLORATION_TOOLS: List[Dict[str, Any]] = [
    _SUBMIT_QUERY_TOOL,
    _FINISH_EXPLORATION_TOOL,
]
RESPONSES_TEST_TOOLS: List[Dict[str, Any]] = [_SUBMIT_FINAL_ANSWER_TOOL]
RESPONSES_TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    *RESPONSES_EXPLORATION_TOOLS,
    *RESPONSES_TEST_TOOLS,
]

OPENAI_CHAT_TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["parameters"],
        },
    }
    for tool in RESPONSES_TOOL_DEFINITIONS
]

OPENAI_CHAT_EXPLORATION_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["parameters"],
        },
    }
    for tool in RESPONSES_EXPLORATION_TOOLS
]

OPENAI_CHAT_TEST_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["parameters"],
        },
    }
    for tool in RESPONSES_TEST_TOOLS
]


def responses_tools_for_phase(phase: str) -> List[Dict[str, Any]]:
    """Exploration exposes query + finish; testing exposes submit_final_answer only."""
    if phase == "test":
        return RESPONSES_TEST_TOOLS
    return RESPONSES_EXPLORATION_TOOLS


def chat_tools_for_phase(phase: str) -> List[Dict[str, Any]]:
    if phase == "test":
        return OPENAI_CHAT_TEST_TOOLS
    return OPENAI_CHAT_EXPLORATION_TOOLS


def _system_prompt(session: ActiveArcTrialSession) -> str:
    lines = [
        "You are solving a grid transformation task by actively querying the underlying "
        "transformation rule by submitting input grids to the environment.",
        "",
        "Rules:",
        "- In the following, you are given a single example pair consisting of an "
        "input-output grid pair. Grids use integer values 0-9 to represent color.",
        "- You can use the submit_query tool to submit an input grid. Once you have finished "
        "exploration, you can use the finish_exploration tool to move to the testing stage.",
        "- A wrong final test answer returns you to the exploration stage and adds +10 to "
        "the query count.",
        "- Your performance will be scored based on the amount of queries you need.",
    ]
    if session.noisy_science:
        lines.insert(
            -1,
            f"- Query outputs may be randomly corrupted (p≈{session.noise_probability:.2f}); "
            "trust patterns across queries.",
        )
    if not session.re_trials:
        lines = [ln for ln in lines if "+10" not in ln]
    return "\n".join(lines)


def _primary_training_pair(session: ActiveArcTrialSession) -> Optional[Dict[str, List[List[int]]]]:
    pair = None
    if session.hot_start and session.hot_start_pair is not None:
        pair = session.hot_start_pair
    elif session.task.train_pairs:
        pair = session.task.train_pairs[0]
    if pair is None:
        return None
    return {"input": clone_grid(pair.input), "output": clone_grid(pair.output)}


def build_initial_responses_input(session: ActiveArcTrialSession) -> List[Dict[str, str]]:
    """Turn-1 input: persistent developer rules + user task (replayed via ``previous_response_id``)."""
    return [
        {"role": "developer", "content": _system_prompt(session)},
        {"role": "user", "content": build_task_user_message(session)},
    ]


def build_task_user_message(session: ActiveArcTrialSession) -> str:
    training_pair = _primary_training_pair(session)
    payload = {
        "task_id": session.task_id,
        "training_pair": training_pair,
    }
    return (
        "Here is your task (JSON). Test inputs are hidden until you call finish_exploration.\n\n"
        f"```json\n{json.dumps(payload, indent=2)}\n```"
    )


def test_phase_tool_required_message(*, assistant_text: Optional[str] = None) -> str:
    """User-turn reminder when the model replies in plain text during testing."""
    preview = ""
    if assistant_text and assistant_text.strip():
        preview = (
            f"\n\nYour message ({assistant_text.strip()!r}) was not accepted as a final answer."
        )
    return (
        "Testing stage: answers must be submitted via a tool call, not plain text."
        f"{preview}\n\n"
        "Call submit_final_answer with a JSON object "
        '{"grid": [[...], ...]} — a rectangular matrix the same shape as '
        "test_input_grid, each cell an integer 0–9."
    )


def execute_tool_call(
    session: ActiveArcTrialSession,
    name: str,
    arguments: Optional[str],
) -> Dict[str, Any]:
    args: Dict[str, Any] = {}
    if arguments:
        try:
            args = json.loads(arguments)
        except json.JSONDecodeError as e:
            return {"ok": False, "error": f"Invalid JSON arguments: {e}"}

    if name == "submit_query":
        grid = args.get("grid")
        if not isinstance(grid, list):
            return {"ok": False, "error": "Missing or invalid grid for submit_query."}
        return session.submit_query(grid)

    if name == "finish_exploration":
        return session.finish_exploration()

    if name == "submit_final_answer":
        grid = args.get("grid")
        if not isinstance(grid, list):
            return {"ok": False, "error": "Missing or invalid grid for submit_final_answer."}
        return session.submit_final_answer(grid)

    return {"ok": False, "error": f"Unknown tool: {name}"}
