"""OpenAI Chat Completions loop with ActiveARC tools (legacy backend)."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from framework.active_arc.headless_trial import ActiveArcTrialSession
from framework.prompting.active_arc_tools import (
    DEFAULT_OPENAI_MODEL,
    OPENAI_CHAT_TOOL_DEFINITIONS,
    _system_prompt,
    build_task_user_message,
    chat_tools_for_phase,
    execute_tool_call,
    test_phase_tool_required_message,
)

# Backward-compatible re-exports
OPENAI_TOOL_DEFINITIONS = OPENAI_CHAT_TOOL_DEFINITIONS


def run_openai_agent_loop(
    session: ActiveArcTrialSession,
    *,
    model: Optional[str] = None,
    max_turns: int = 64,
    temperature: float = 0.2,
) -> Dict[str, Any]:
    """Run OpenAI Chat Completions tool loop until done, stop, or max_turns."""
    try:
        from openai import OpenAI
    except ImportError as e:
        raise ImportError("Install the OpenAI SDK: pip install openai") from e

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY in the environment.")

    resolved_model = model or os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)

    client = OpenAI(api_key=api_key)
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": _system_prompt(session)},
        {"role": "user", "content": build_task_user_message(session)},
    ]

    transcript: List[Dict[str, Any]] = []
    last_result: Dict[str, Any] = {
        "session": session,
        "transcript": transcript,
        "backend": "chat",
        "model": resolved_model,
        "final": None,
    }

    for turn in range(max_turns):
        response = client.chat.completions.create(
            model=resolved_model,
            messages=messages,
            tools=chat_tools_for_phase(session.phase),
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
            if session.phase == "test":
                reminder = test_phase_tool_required_message(assistant_text=msg.content)
                transcript[-1]["tool_results"].append(
                    {
                        "name": "_protocol_reminder",
                        "result": {"ok": False, "error": reminder},
                    }
                )
                messages.append({"role": "user", "content": reminder})
                continue
            last_result["final"] = {
                "reason": "model_stop",
                "message": msg.content,
                "phase": session.phase,
            }
            return last_result

        for tc in msg.tool_calls:
            name = tc.function.name
            out = execute_tool_call(session, name, tc.function.arguments)
            transcript[-1]["tool_results"].append({"name": name, "result": out})

            if name == "submit_final_answer" and out.get("ok") and out.get("done"):
                last_result["final"] = {
                    "reason": "trial_complete",
                    "result": out,
                    "query_count": session.query_count,
                    "correct": out.get("correct"),
                }
                return last_result

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(out),
                }
            )

    last_result["final"] = {
        "reason": "max_turns",
        "phase": session.phase,
        "query_count": session.query_count,
    }
    return last_result
