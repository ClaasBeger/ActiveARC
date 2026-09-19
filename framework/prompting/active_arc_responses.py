"""Responses API loop for ActiveARC (recommended multi-turn backend).

State is threaded by ResponsesConversation: on OpenAI, ``previous_response_id``
keeps reasoning and call context server-side and each turn sends only the new
``function_call_output`` items; on OpenRouter, which holds no state, the whole
conversation is replayed in ``input``. Stable rules live in a turn-1
``developer`` message either way.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from framework.active_arc.headless_trial import ActiveArcTrialSession
from framework.prompting.active_arc_tools import (
    DEFAULT_OPENAI_MODEL,  # noqa: F401  (re-exported for callers)
    build_initial_responses_input,
    REQUEST_TEST_TOOL_NAMES,
    execute_tool_call,
    plain_text_protocol_reminder,
    responses_tools_for_phase,
)
from framework.prompting.clients import (
    ResponsesConversation,
    build_client,
    resolve_model,
    resolve_provider,
    resolve_store,
    responses_extras,
    supports_responses_api,
)
from framework.prompting.branch_test import run_branched_test
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
    provider: Optional[str] = None,
    max_output_tokens: Optional[int] = None,
) -> Dict[str, Any]:
    """Run an ActiveARC trial via the OpenAI Responses API + custom function tools."""
    resolved_provider = resolve_provider(provider, model)
    if not supports_responses_api(resolved_provider):
        raise RuntimeError(
            f"Provider {resolved_provider!r} does not implement the Responses API; "
            "run this model with --backend chat."
        )
    resolved_model = resolve_model(resolved_provider, model)
    client = build_client(resolved_provider)
    store = resolve_store(resolved_provider, store)

    transcript: List[Dict[str, Any]] = []
    last_result: Dict[str, Any] = {
        "session": session,
        "transcript": transcript,
        "backend": "responses",
        "provider": resolved_provider,
        "model": resolved_model,
        "reasoning_effort": reasoning_effort,
        "final": None,
        "usage": None,
    }

    convo = ResponsesConversation(
        resolved_provider, build_initial_responses_input(session)
    )

    for turn in range(max_turns):
        create_kwargs: Dict[str, Any] = {
            "model": resolved_model,
            "tools": responses_tools_for_phase(
                session.phase,
                program_mode=session.program_test,
                n_test_items=len(session.test_items) or 1,
            ),
            "store": store,
            **convo.create_kwargs(),
        }
        create_kwargs.update(
            responses_extras(resolved_provider, resolved_model, reasoning_effort)
        )
        if max_output_tokens is not None:
            create_kwargs["max_output_tokens"] = max_output_tokens

        response = client.responses.create(**create_kwargs)
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
        convo.record_turn(
            response,
            [_function_call_fields(item) for item in function_calls],
            assistant_text=_assistant_text(response),
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
                convo.extend([{"role": "user", "content": reminder}])
                continue
            last_result["usage"] = usage_totals(transcript)
            last_result["final"] = {
                "reason": "model_stop",
                "message": assistant_text,
                "phase": session.phase,
            }
            return last_result

        tool_outputs: List[Any] = []
        for item in function_calls:
            call_id, name, arguments = _function_call_fields(item)
            out = execute_tool_call(session, name, arguments)
            transcript[-1]["tool_results"].append({"name": name, "result": out})

            if out.get("sampler_exhausted"):
                last_result["usage"] = usage_totals(transcript)
                last_result["final"] = {
                    "reason": "sampler_exhausted",
                    "message": out.get("message"),
                    "phase": out.get("phase", session.phase),
                    "query_count": session.query_count,
                }
                return last_result

            if (name in REQUEST_TEST_TOOL_NAMES and out.get("ok")
                    and session.phase == "test" and not session.program_test):
                # Close out request_test before branching: a fork inherits this
                # turn, and a function_call with no output is rejected outright.
                convo.extend(tool_outputs + [{
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(out),
                }])
                final = run_branched_test(
                    client, session, convo, model=resolved_model,
                    reasoning_effort=reasoning_effort, store=store,
                    max_turns=8, transcript=transcript,
                )
                last_result["usage"] = usage_totals(transcript)
                last_result["final"] = {
                    "reason": "trial_complete",
                    "result": final,
                    "query_count": session.query_count,
                    "correct": final.get("correct"),
                }
                return last_result

            if name in ("submit_final_answer", "submit_program") and out.get("ok") and out.get("done"):
                last_result["usage"] = usage_totals(transcript)
                last_result["final"] = {
                    "reason": "trial_complete",
                    "result": out,
                    "query_count": session.query_count,
                    "correct": out.get("correct"),
                }
                return last_result

            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(out),
                }
            )
        convo.extend(tool_outputs)

    last_result["usage"] = usage_totals(transcript)
    last_result["final"] = {
        "reason": "max_turns",
        "phase": session.phase,
        "query_count": session.query_count,
    }
    return last_result
