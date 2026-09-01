"""OpenAI Responses API loop for ActiveARC (recommended multi-turn backend).

Uses ``previous_response_id`` to chain tool turns so reasoning and call context
stay server-side. Stable rules live in a turn-1 ``developer`` input message (persisted
in the chain); later turns send only new ``function_call_output`` items.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from framework.active_arc.headless_trial import ActiveArcTrialSession
from framework.prompting.active_arc_tools import (
    DEFAULT_OPENAI_MODEL,
    build_initial_responses_input,
    execute_tool_call,
    plain_text_protocol_reminder,
    responses_tools_for_phase,
)
from framework.prompting.response_logging import summarize_response, usage_totals


def _output_item_type(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("type", ""))
    return str(getattr(item, "type", ""))


def _function_call_fields(item: Any) -> tuple[str, str, str]:
    if isinstance(item, dict):
        return (
            str(item.get("call_id", "")),
            str(item.get("name", "")),
            str(item.get("arguments", "")),
        )
    return (
        str(getattr(item, "call_id", "")),
        str(getattr(item, "name", "")),
        str(getattr(item, "arguments", "")),
    )


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
            if isinstance(block, dict):
                txt = block.get("text")
            else:
                txt = getattr(block, "text", None)
            if isinstance(txt, str) and txt.strip():
                parts.append(txt)
    return "\n".join(parts).strip() or None


def run_active_arc_responses_loop(
    session: ActiveArcTrialSession,
    *,
    model: Optional[str] = None,
    max_turns: int = 64,
    reasoning_effort: Optional[str] = "low",
    store: bool = True,
) -> Dict[str, Any]:
    """Run an ActiveARC trial via the OpenAI Responses API + custom function tools."""
    try:
        from openai import OpenAI
    except ImportError as e:
        raise ImportError("Install the OpenAI SDK: pip install openai") from e

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY in the environment.")

    resolved_model = model or os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    client = OpenAI(api_key=api_key)

    transcript: List[Dict[str, Any]] = []
    last_result: Dict[str, Any] = {
        "session": session,
        "transcript": transcript,
        "backend": "responses",
        "model": resolved_model,
        "reasoning_effort": reasoning_effort,
        "final": None,
        "usage": None,
    }

    previous_response_id: Optional[str] = None
    pending_input: List[Any] = build_initial_responses_input(session)

    for turn in range(max_turns):
        create_kwargs: Dict[str, Any] = {
            "model": resolved_model,
            "tools": responses_tools_for_phase(session.phase),
            "input": pending_input,
            "store": store,
        }
        if reasoning_effort is not None:
            create_kwargs["reasoning"] = {"effort": reasoning_effort}
        if previous_response_id is not None:
            create_kwargs["previous_response_id"] = previous_response_id

        response = client.responses.create(**create_kwargs)
        previous_response_id = response.id
        response_log = summarize_response(response)

        function_calls = [
            item
            for item in (getattr(response, "output", None) or [])
            if _output_item_type(item) == "function_call"
        ]
        tool_calls_meta = [
            {
                "call_id": _function_call_fields(item)[0],
                "name": _function_call_fields(item)[1],
                "arguments": _function_call_fields(item)[2],
            }
            for item in function_calls
        ]
        transcript.append(
            {
                "turn": turn,
                "phase": session.phase,
                "response_id": response.id,
                "response": response_log,
                "assistant": _assistant_text(response),
                "tool_calls": tool_calls_meta,
                "tool_results": [],
            }
        )

        if not function_calls:
            assistant_text = _assistant_text(response)
            reminder = plain_text_protocol_reminder(session, assistant_text=assistant_text)
            if reminder is not None:
                transcript[-1]["tool_results"].append(
                    {
                        "name": "_protocol_reminder",
                        "result": {"ok": False, "error": reminder},
                    }
                )
                pending_input = [{"role": "user", "content": reminder}]
                continue
            last_result["usage"] = usage_totals(transcript)
            last_result["final"] = {
                "reason": "model_stop",
                "message": assistant_text,
                "phase": session.phase,
            }
            return last_result

        pending_input = []
        for item in function_calls:
            call_id, name, arguments = _function_call_fields(item)
            out = execute_tool_call(session, name, arguments)
            transcript[-1]["tool_results"].append({"name": name, "result": out})

            if name == "submit_final_answer" and out.get("ok") and out.get("done"):
                last_result["usage"] = usage_totals(transcript)
                last_result["final"] = {
                    "reason": "trial_complete",
                    "result": out,
                    "query_count": session.query_count,
                    "correct": out.get("correct"),
                }
                return last_result

            pending_input.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(out),
                }
            )

    last_result["usage"] = usage_totals(transcript)
    last_result["final"] = {
        "reason": "max_turns",
        "phase": session.phase,
        "query_count": session.query_count,
    }
    return last_result
