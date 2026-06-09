"""OpenAI Chat Completions loop with ActiveARC tools (submit_query, finish_exploration, submit_final_answer)."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from framework.active_arc.headless_trial import ActiveArcTrialSession

OPENAI_TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "submit_query",
            "description": (
                "Exploration phase only. Submit an input grid; the hidden verifier returns an output grid. "
                "Each successful call increases your query count (score) by 1. "
                "If every verifier errors on this input, the call fails and does not count."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "grid": {
                        "type": "array",
                        "description": "Rectangular matrix; each cell is an integer color 0–9.",
                        "items": {
                            "type": "array",
                            "items": {"type": "integer", "minimum": 0, "maximum": 9},
                        },
                    }
                },
                "required": ["grid"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finish_exploration",
            "description": (
                "End exploration and receive the held-out test input grid (ARC-GEN dynamic pair). "
                "You cannot submit more queries until you have handled a wrong test answer with re-trials "
                "(if enabled). After this, use submit_final_answer with your predicted output."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_final_answer",
            "description": (
                "Test phase only. Submit your predicted output grid for the test input. "
                "Does not add to query count unless re-trials applies +10 after a wrong answer."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "grid": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "integer", "minimum": 0, "maximum": 9},
                        },
                    }
                },
                "required": ["grid"],
            },
        },
    },
]


def _system_prompt(session: ActiveArcTrialSession) -> str:
    flags = []
    if session.hot_start:
        flags.append("hot_start: one free training pair is shown in the task JSON (no query cost).")
    if session.noisy_science:
        flags.append(
            f"noisy_science: query outputs may be randomly corrupted (p≈{session.noise_probability:.2f}); "
            "trust patterns across queries."
        )
    if session.re_trials:
        flags.append(
            "re_trials: a wrong final test answer returns you to exploration and adds +10 to the query count; "
            "you may query again and call finish_exploration to retry the same test."
        )
    flag_text = "\n".join(f"- {f}" for f in flags) if flags else "- baseline (no extra modes)."
    return f"""You are solving an ARC-style task by active querying.

Rules:
- Training pairs show the transformation. Integer grids use colors 0–9.
- Lower query_count is better when you eventually get the test right.
- You do not see the reference program; only tool outputs.
- Use submit_query to explore. When ready, finish_exploration to get the test input, then submit_final_answer.

Modes for this trial:
{flag_text}

Respond by calling tools until you have submitted a final answer and the environment reports phase done (or you hit the turn limit).
"""


def build_task_user_message(session: ActiveArcTrialSession) -> str:
    payload = {
        "task_id": session.task_id,
        "training_pairs": session.train_pairs_json(),
        "hot_start_free_pair": session.hot_start_json(),
    }
    return (
        "Here is your task (JSON). The test input is hidden until you call finish_exploration.\n\n"
        f"```json\n{json.dumps(payload, indent=2)}\n```"
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


def run_openai_agent_loop(
    session: ActiveArcTrialSession,
    *,
    model: Optional[str] = None,
    max_turns: int = 64,
    temperature: float = 0.2,
) -> Dict[str, Any]:
    """Run OpenAI tool loop until done, stop, or max_turns. Requires ``openai`` package and ``OPENAI_API_KEY``."""
    try:
        from openai import OpenAI
    except ImportError as e:
        raise ImportError(
            "Install the OpenAI SDK: pip install openai"
        ) from e

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY in the environment.")

    resolved_model = model or os.environ.get("OPENAI_MODEL", "gpt-4o")

    client = OpenAI(api_key=api_key)
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": _system_prompt(session)},
        {"role": "user", "content": build_task_user_message(session)},
    ]

    transcript: List[Dict[str, Any]] = []
    last_result: Dict[str, Any] = {
        "session": session,
        "transcript": transcript,
        "final": None,
    }

    for turn in range(max_turns):
        response = client.chat.completions.create(
            model=resolved_model,
            messages=messages,
            tools=OPENAI_TOOL_DEFINITIONS,
            tool_choice="auto",
            temperature=temperature,
        )
        choice = response.choices[0]
        msg = choice.message
        tool_calls_meta = [
            {
                "id": tc.id,
                "name": tc.function.name,
                "arguments": tc.function.arguments,
            }
            for tc in (msg.tool_calls or [])
        ]
        transcript.append(
            {
                "turn": turn,
                "assistant": msg.content,
                "tool_calls": tool_calls_meta,
                "tool_results": [],
            }
        )

        # Append assistant message (OpenAI expects tool_calls preserved)
        assistant_msg: Dict[str, Any] = {
            "role": "assistant",
            "content": msg.content,
        }
        if msg.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]
        messages.append(assistant_msg)

        if not msg.tool_calls:
            last_result["final"] = {
                "reason": "model_stop",
                "message": msg.content,
                "phase": session.phase,
            }
            return last_result

        for tc in msg.tool_calls:
            name = tc.function.name
            out = execute_tool_call(session, name, tc.function.arguments)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(out),
                }
            )
            transcript[-1]["tool_results"].append({"name": name, "result": out})

            if name == "submit_final_answer" and out.get("ok") and out.get("done"):
                last_result["final"] = {
                    "reason": "trial_complete",
                    "result": out,
                    "query_count": session.query_count,
                    "correct": out.get("correct"),
                }
                return last_result

    last_result["final"] = {
        "reason": "max_turns",
        "phase": session.phase,
        "query_count": session.query_count,
    }
    return last_result
