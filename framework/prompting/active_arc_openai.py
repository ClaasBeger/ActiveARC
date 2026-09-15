"""Chat Completions loop with ActiveARC tools.

Also the OpenRouter path: OpenRouter speaks Chat Completions but not the
Responses API, so Anthropic and Google models run this loop.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from framework.active_arc.headless_trial import ActiveArcTrialSession
from framework.prompting.active_arc_tools import (
    OPENAI_CHAT_TOOL_DEFINITIONS,
    _system_prompt,
    build_task_user_message,
    chat_tools_for_phase,
    execute_tool_call,
    plain_text_protocol_reminder,
)
from framework.prompting.clients import (
    build_client,
    reasoning_extra_body,
    resolve_model,
    resolve_provider,
)
from framework.prompting.response_logging import (
    chat_usage_to_responses_shape,
    usage_totals,
)

# Backward-compatible re-exports
OPENAI_TOOL_DEFINITIONS = OPENAI_CHAT_TOOL_DEFINITIONS


def run_openai_agent_loop(
    session: ActiveArcTrialSession,
    *,
    model: Optional[str] = None,
    max_turns: int = 64,
    temperature: float = 0.2,
    provider: Optional[str] = None,
    reasoning_effort: Optional[str] = None,
) -> Dict[str, Any]:
    """Run a Chat Completions tool loop until done, stop, or max_turns."""
    resolved_provider = resolve_provider(provider, model)
    resolved_model = resolve_model(resolved_provider, model)
    client = build_client(resolved_provider)
    extra_body = reasoning_extra_body(resolved_provider, reasoning_effort)

    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": _system_prompt(session)},
        {"role": "user", "content": build_task_user_message(session)},
    ]

    transcript: List[Dict[str, Any]] = []
    last_result: Dict[str, Any] = {
        "session": session,
        "transcript": transcript,
        "backend": "chat",
        "provider": resolved_provider,
        "model": resolved_model,
        "reasoning_effort": reasoning_effort,
        "final": None,
        "usage": None,
    }

    def _finish(final: Dict[str, Any]) -> Dict[str, Any]:
        last_result["final"] = final
        last_result["usage"] = usage_totals(transcript)
        return last_result

    for turn in range(max_turns):
        create_kwargs: Dict[str, Any] = {
            "model": resolved_model,
            "messages": messages,
            "tools": chat_tools_for_phase(
                session.phase, program_mode=session.program_test
            ),
            "tool_choice": "auto",
            "temperature": temperature,
        }
        if extra_body:
            create_kwargs["extra_body"] = extra_body
        response = client.chat.completions.create(**create_kwargs)
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
                "usage": chat_usage_to_responses_shape(
                    getattr(response, "usage", None)
                ),
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
            reminder = plain_text_protocol_reminder(session, assistant_text=msg.content)
            if reminder is not None:
                transcript[-1]["tool_results"].append(
                    {
                        "name": "_protocol_reminder",
                        "result": {"ok": False, "error": reminder},
                    }
                )
                messages.append({"role": "user", "content": reminder})
                continue
            return _finish(
                {
                    "reason": "model_stop",
                    "message": msg.content,
                    "phase": session.phase,
                }
            )

        for tc in msg.tool_calls:
            name = tc.function.name
            out = execute_tool_call(session, name, tc.function.arguments)
            transcript[-1]["tool_results"].append({"name": name, "result": out})

            if out.get("sampler_exhausted"):
                return _finish(
                    {
                        "reason": "sampler_exhausted",
                        "message": out.get("message"),
                        "phase": out.get("phase", session.phase),
                        "query_count": session.query_count,
                    }
                )

            if name in ("submit_final_answer", "submit_program") and out.get("ok") and out.get("done"):
                return _finish(
                    {
                        "reason": "trial_complete",
                        "result": out,
                        "query_count": session.query_count,
                        "correct": out.get("correct"),
                    }
                )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(out),
                }
            )

    return _finish(
        {
            "reason": "max_turns",
            "phase": session.phase,
            "query_count": session.query_count,
        }
    )
