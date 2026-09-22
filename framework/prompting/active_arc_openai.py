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
    REQUEST_TEST_TOOL_NAMES,
    _system_prompt,
    build_task_user_message,
    chat_tools_for_phase,
    execute_tool_call,
    plain_text_protocol_reminder,
)
from framework.prompting.clients import (
    PROVIDER_OPENROUTER,
    build_client,
    cache_control_block,
    provider_routing,
    reasoning_extra_body,
    resolve_model,
    resolve_provider,
)
from framework.prompting.branch_test import (
    MAX_CONSECUTIVE_STALLS,
    MAX_TOTAL_STALLS,
    run_branched_test_chat,
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
    pin_provider: bool = True,
    prompt_cache: bool = False,
    max_output_tokens: Optional[int] = None,
) -> Dict[str, Any]:
    """Run a Chat Completions tool loop until done, stop, or max_turns.

    ``max_output_tokens`` caps one response. Left unset, the provider applies its
    own default, which it also reserves against the context window whether or not
    the model uses it -- and a model that falls into a repetition loop will emit
    exactly that default, turn after turn, until the conversation no longer fits.
    """
    resolved_provider = resolve_provider(provider, model)
    resolved_model = resolve_model(resolved_provider, model)
    client = build_client(resolved_provider)
    extra_body = dict(reasoning_extra_body(resolved_provider, reasoning_effort))
    if pin_provider and resolved_provider == PROVIDER_OPENROUTER:
        extra_body["provider"] = provider_routing(resolved_model)

    system_prompt = _system_prompt(session)
    messages: List[Dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                [cache_control_block(system_prompt)] if prompt_cache else system_prompt
            ),
        },
        {"role": "user", "content": build_task_user_message(session)},
    ]

    transcript: List[Dict[str, Any]] = []
    consecutive_stalls = 0
    total_stalls = 0
    last_result: Dict[str, Any] = {
        "session": session,
        "transcript": transcript,
        "backend": "chat",
        "provider": resolved_provider,
        "model": resolved_model,
        "reasoning_effort": reasoning_effort,
        "provider_routing": extra_body.get("provider"),
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
                session.phase,
                program_mode=session.program_test,
                n_test_items=len(session.test_items) or 1,
            ),
            "tool_choice": "auto",
            "temperature": temperature,
        }
        if max_output_tokens is not None:
            create_kwargs["max_tokens"] = max_output_tokens
        if extra_body:
            create_kwargs["extra_body"] = extra_body
        # Read the raw body: the SDK's typed message drops reasoning_details,
        # which is exactly the field that has to go back for the model to keep
        # its own thinking across turns.
        raw = client.chat.completions.with_raw_response.create(**create_kwargs)
        payload = json.loads(raw.text)
        msg = payload["choices"][0]["message"]
        raw_tool_calls = msg.get("tool_calls") or []
        tool_calls_meta = [
            {
                "id": tc.get("id"),
                "name": (tc.get("function") or {}).get("name"),
                "arguments": (tc.get("function") or {}).get("arguments"),
            }
            for tc in raw_tool_calls
        ]
        transcript.append(
            {
                "turn": turn,
                "assistant": msg.get("content"),
                "tool_calls": tool_calls_meta,
                "tool_results": [],
                "n_reasoning_details": len(msg.get("reasoning_details") or []),
                "usage": chat_usage_to_responses_shape(payload.get("usage")),
            }
        )

        # Replayed verbatim, reasoning_details included: anything rebuilt from
        # parsed fields loses the signed reasoning and the model restarts its
        # thinking every turn.
        #
        # Unless the turn was cut off mid-thought with nothing to act on. Then
        # replaying it hands the model an unfinished thought to resume, which it
        # does, and is cut off again -- a loop that adds the whole output cap to
        # the context every turn until the window is gone. Dropping it lets the
        # next turn start the thought over instead of continuing it.
        truncated = (payload["choices"][0] or {}).get("finish_reason") == "length"
        stalled = truncated and not raw_tool_calls
        if stalled:
            transcript[-1]["dropped_truncated_reasoning"] = True
            consecutive_stalls += 1
            total_stalls += 1
        else:
            messages.append(json.loads(json.dumps(msg)))
            consecutive_stalls = 0

        # A run of stalls back to back is the obvious case. The subtler one is a
        # trial that interleaves them with real tool calls, so the consecutive
        # count keeps resetting while the transcript fills with capped turns that
        # produced nothing -- seventeen of them in one observed trial. Count both.
        if consecutive_stalls >= MAX_CONSECUTIVE_STALLS or total_stalls >= MAX_TOTAL_STALLS:
            return _finish({
                "reason": "reasoning_runaway",
                "message": (
                    f"{consecutive_stalls} consecutive and {total_stalls} total turns "
                    "hit the output cap while still reasoning and produced no tool call."
                ),
                "consecutive_stalls": consecutive_stalls,
                "total_stalls": total_stalls,
                "phase": session.phase,
                "query_count": session.query_count,
            })

        if not raw_tool_calls:
            reminder = plain_text_protocol_reminder(session, assistant_text=msg.get("content"))
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
                    "message": msg.get("content"),
                    "phase": session.phase,
                }
            )

        for tc in raw_tool_calls:
            fn = tc.get("function") or {}
            name = fn.get("name")
            out = execute_tool_call(session, name, fn.get("arguments"))
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

            if (name in REQUEST_TEST_TOOL_NAMES and out.get("ok")
                    and session.phase == "test" and not session.program_test):
                # Close out request_test before branching: a branch copies this
                # message list, and a tool_call with no reply is rejected.
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id"),
                    "content": json.dumps(out),
                })
                final = run_branched_test_chat(
                    client, session, messages, model=resolved_model,
                    extra_body=extra_body, temperature=temperature,
                    max_turns=8, transcript=transcript,
                    max_output_tokens=max_output_tokens,
                )
                return _finish({
                    "reason": "trial_complete",
                    "result": final,
                    "query_count": session.query_count,
                    "correct": final.get("correct"),
                })

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
                    "tool_call_id": tc.get("id"),
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
