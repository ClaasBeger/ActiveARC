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
        "Exploration stage only. Ask for another example: submit an input grid; "
        "the environment returns the transformed output grid. "
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

_REQUEST_TEST_TOOL: Dict[str, Any] = {
    "type": "function",
    "name": "request_test",
    "description": (
        "Exploration stage only. Request the final test and receive a held-out test input grid."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
    "strict": True,
}

# Legacy tool name from earlier protocol; still dispatched.
REQUEST_TEST_TOOL_NAMES = frozenset({"request_test", "finish_exploration"})

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

_SUBMIT_PROGRAM_TOOL: Dict[str, Any] = {
    "type": "function",
    "name": "submit_program",
    "description": (
        "Testing stage only (program trials). Submit a Python program implementing the "
        "transformation rule. Define transform(grid) taking a grid (list of rows of "
        "integers 0-9) and returning the transformed grid. Standard library only; no "
        "input/output. It is run on held-out examples, so it must implement the general "
        "rule rather than special-case the grids you have seen."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python source defining transform(grid) -> grid.",
            }
        },
        "required": ["code"],
        "additionalProperties": False,
    },
    "strict": True,
}

RESPONSES_EXPLORATION_TOOLS: List[Dict[str, Any]] = [
    _SUBMIT_QUERY_TOOL,
    _REQUEST_TEST_TOOL,
]
RESPONSES_TEST_TOOLS: List[Dict[str, Any]] = [_SUBMIT_FINAL_ANSWER_TOOL]
RESPONSES_PROGRAM_TEST_TOOLS: List[Dict[str, Any]] = [_SUBMIT_PROGRAM_TOOL]
RESPONSES_TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    *RESPONSES_EXPLORATION_TOOLS,
    *RESPONSES_TEST_TOOLS,
    *RESPONSES_PROGRAM_TEST_TOOLS,
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

OPENAI_CHAT_PROGRAM_TEST_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["parameters"],
        },
    }
    for tool in RESPONSES_PROGRAM_TEST_TOOLS
]


def responses_tools_for_phase(
    phase: str, *, program_mode: bool = False
) -> List[Dict[str, Any]]:
    """Exploration exposes query + request_test; testing exposes the answer tool.

    ``program_mode`` swaps ``submit_final_answer`` for ``submit_program``.
    """
    if phase == "test":
        return RESPONSES_PROGRAM_TEST_TOOLS if program_mode else RESPONSES_TEST_TOOLS
    return RESPONSES_EXPLORATION_TOOLS


def chat_tools_for_phase(phase: str, *, program_mode: bool = False) -> List[Dict[str, Any]]:
    if phase == "test":
        return OPENAI_CHAT_PROGRAM_TEST_TOOLS if program_mode else OPENAI_CHAT_TEST_TOOLS
    return OPENAI_CHAT_EXPLORATION_TOOLS


def _system_prompt(session: ActiveArcTrialSession) -> str:
    lines = [
        "- In the following, you are given a single example consisting of an "
        "input-output grid pair. There is an abstract rule that describes the "
        "transformation from the input grid to the output grid. Your task is to "
        "determine this abstract rule, over a series of steps.",
        "",
        (
            "At each step, you may either (1) make a query: i.e., ask for another "
            "example of an input-output grid pair that follows the same rule, or, "
            "(2) if you are confident you know the rule, you may ask for a test, in "
            "which you will submit a Python program implementing the rule."
            if session.program_test
            else "At each step, you may either (1) make a query: i.e., ask for another "
            "example of an input-output grid pair that follows the same rule, or, "
            "(2) if you are confident you know the rule, you may ask for a test, in "
            "which you will be given a new input grid, and you will need to apply "
            "the rule to generate the correct output grid."
        ),
        "",
        "- You can use the submit_query tool to ask for an input grid. Once you "
        "are confident you know the rule, you can use the request_test tool to "
        "request the final test.",
    ]
    if session.program_test:
        lines.extend(
            [
                "- Submit the program with submit_program: define transform(grid) "
                "taking a grid (list of rows of integers 0-9) and returning the "
                "transformed grid. Standard library only.",
                "- Your program is run on held-out examples of this same rule, so it "
                "must implement the general transformation rather than special-case the "
                "grids you have seen. It counts as correct only if it reproduces every "
                "held-out example.",
                "- Format:",
                "",
                "```python",
                "def transform(grid):",
                "    # grid is a list of rows, e.g. [[0, 1, 0], [5, 5, 0]]",
                "    # return the transformed grid in the same format",
                "    return [row[:] for row in grid]",
                "```",
                "",
                "- Your performance will be scored based on the number of queries you "
                "submit and whether your program is correct.",
            ]
        )
    else:
        lines.append(
            "- Your performance will be scored based on the number of queries you "
            "submit and whether you generate a correct output grid when you are given "
            "a test."
        )
    penalty = session.announced_wrong_answer_penalty()
    if penalty > 0:
        if session.re_trials:
            lines.append(
                f"- A wrong test answer returns you to exploration and adds +{penalty} "
                "to your query count."
            )
        else:
            lines.append(
                f"- A wrong test answer adds +{penalty} to your query count."
            )
    if session.noisy_science:
        lines.append(
            f"- Query outputs may be randomly corrupted (p≈{session.noise_probability:.2f}); "
            "trust patterns across queries."
        )
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
    payload = {"training_pair": training_pair}
    return (
        "Here is your input-output grid pair (JSON).\n\n"
        f"```json\n{json.dumps(payload, indent=2)}\n```"
    )


def looks_like_raw_grid(text: Optional[str]) -> bool:
    """True when plain text looks like a pasted grid row or matrix (e.g. [], [0,1], [[0,1],...])."""
    if not text:
        return False
    s = text.strip()
    if not s.startswith("["):
        return False
    try:
        parsed = json.loads(s)
    except json.JSONDecodeError:
        if s.startswith("[[") and "," in s:
            return True
        if "," in s:
            return any(ch.isdigit() for ch in s)
        return False
    if not isinstance(parsed, list):
        return False
    if not parsed:
        return True
    if all(isinstance(cell, int) for cell in parsed):
        return True
    if all(isinstance(row, list) for row in parsed):
        return True
    return False


def explore_phase_grid_dump_message(*, assistant_text: Optional[str] = None) -> str:
    """User-turn reminder when the model pastes a grid in plain text during exploration."""
    preview = ""
    if assistant_text and assistant_text.strip():
        trimmed = assistant_text.strip()
        if len(trimmed) > 80:
            trimmed = trimmed[:77] + "..."
        preview = f"\n\nYour message ({trimmed!r}) was not accepted as a tool call."
    return (
        "Exploration stage: do not paste grids as plain text."
        f"{preview}\n\n"
        "Use submit_query with a JSON object "
        '{"grid": [[...], ...]} to query the environment, or call request_test '
        "when you are ready for the held-out test input."
    )


def plain_text_protocol_reminder(
    session: ActiveArcTrialSession,
    *,
    assistant_text: Optional[str] = None,
) -> Optional[str]:
    """What to say back when a turn produced no tool call.

    A pasted grid gets the phase-specific correction. Anything else -- prose,
    or a turn that came back with nothing but a reasoning item and no message
    at all -- gets a nudge naming the tools that move the trial forward. A
    response with no tool call is not an answer and is not a decision to stop,
    so the caller keeps going; only its turn budget ends a trial without one.
    """
    if looks_like_raw_grid(assistant_text):
        if session.phase == "test":
            return test_phase_tool_required_message(
                assistant_text=assistant_text, program_mode=session.program_test
            )
        if session.phase == "explore":
            return explore_phase_grid_dump_message(assistant_text=assistant_text)
    return no_tool_call_message(session, assistant_text=assistant_text)


def no_tool_call_message(
    session: ActiveArcTrialSession, *, assistant_text: Optional[str] = None
) -> str:
    """Nudge for a turn without a tool call, naming the tools for the current phase."""
    preview = ""
    if assistant_text and assistant_text.strip():
        trimmed = assistant_text.strip()
        if len(trimmed) > 80:
            trimmed = trimmed[:77] + "..."
        preview = f" Your message ({trimmed!r}) reached no tool."
    if session.phase == "test":
        tool = "submit_program" if session.program_test else "submit_final_answer"
        return (
            f"No tool was called.{preview} The trial only advances through tool calls: "
            f"call {tool} with your answer for the test input."
        )
    return (
        f"No tool was called.{preview} The trial only advances through tool calls: "
        "call submit_query with an input grid to ask the oracle, or request_test when "
        "you are ready for the test input."
    )


def test_phase_tool_required_message(
    *, assistant_text: Optional[str] = None, program_mode: bool = False
) -> str:
    """User-turn reminder when the model answers in plain text during testing."""
    preview = ""
    if assistant_text and assistant_text.strip():
        trimmed = assistant_text.strip()
        if len(trimmed) > 80:
            trimmed = trimmed[:77] + "..."
        preview = f"\n\nYour message ({trimmed!r}) was not accepted as a final answer."
    if program_mode:
        return (
            "Testing stage: do not paste code as plain text."
            f"{preview}\n\n"
            "Call submit_program with a JSON object "
            '{"code": "def transform(grid): ..."} — Python source defining '
            "transform(grid) -> grid."
        )
    return (
        "Testing stage: do not paste grids as plain text."
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

    if name in REQUEST_TEST_TOOL_NAMES:
        return session.finish_exploration()

    if name == "submit_program":
        return session.submit_program(args.get("code"))

    if name == "submit_final_answer":
        grid = args.get("grid")
        if not isinstance(grid, list):
            return {"ok": False, "error": "Missing or invalid grid for submit_final_answer."}
        return session.submit_final_answer(grid)

    return {"ok": False, "error": f"Unknown tool: {name}"}
