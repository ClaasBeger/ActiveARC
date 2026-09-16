"""Drive the branched test phase over a Responses-shaped conversation.

Called once exploration ends. Takes a fork of the conversation per held-out
item, so each is answered with the full exploration history and none sees
another item.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from framework.active_arc import test_phase
from framework.active_arc.headless_trial import ActiveArcTrialSession
from framework.prompting.active_arc_tools import responses_tools_for_phase
from framework.prompting.clients import responses_extras
from framework.prompting.response_logging import summarize_response


def _item_type(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("type", ""))
    return str(getattr(item, "type", ""))


def _call_fields(item: Any):
    if isinstance(item, dict):
        return item.get("call_id"), item.get("name"), item.get("arguments")
    return (getattr(item, "call_id", None), getattr(item, "name", None),
            getattr(item, "arguments", None))


def _assistant_text(response: Any) -> Optional[str]:
    t = getattr(response, "output_text", None)
    return t if isinstance(t, str) and t.strip() else None


def run_branched_test(
    client: Any,
    session: ActiveArcTrialSession,
    base_convo: Any,
    *,
    model: str,
    reasoning_effort: Optional[str],
    store: bool,
    max_turns: int,
    transcript: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Answer every test item on its own fork of *base_convo*."""
    per_item: List[bool] = []
    tools = responses_tools_for_phase("test", program_mode=False, n_test_items=1)

    for idx in range(len(session.test_items)):
        convo = base_convo.fork()
        convo.append([{"role": "user", "content": test_phase.test_item_prompt(session, idx)}])
        answered = False

        for turn in range(max_turns):
            kwargs: Dict[str, Any] = {
                "model": model, "tools": tools, "store": store, **convo.create_kwargs()
            }
            kwargs.update(responses_extras(convo.provider, model, reasoning_effort))
            response = client.responses.create(**kwargs)
            calls = [i for i in (getattr(response, "output", None) or [])
                     if _item_type(i) == "function_call"]
            log = {
                "turn": turn, "phase": "test", "test_item": idx,
                "response_id": response.id, "response": summarize_response(response),
                "assistant": _assistant_text(response),
                "tool_calls": [dict(zip(("call_id", "name", "arguments"), _call_fields(c)))
                               for c in calls],
                "tool_results": [],
            }
            transcript.append(log)
            convo.record_turn(response, [_call_fields(c) for c in calls],
                              assistant_text=_assistant_text(response))

            if not calls:
                reminder = ("No answer was submitted. Call submit_final_answer with "
                            '{"grid": [[...], ...]} for this test input.')
                log["tool_results"].append(
                    {"name": "_protocol_reminder", "result": {"ok": False, "error": reminder}})
                convo.extend([{"role": "user", "content": reminder}])
                continue

            outs = []
            for c in calls:
                call_id, name, arguments = _call_fields(c)
                if name != "submit_final_answer":
                    out = {"ok": False, "error": f"Unknown tool: {name}"}
                else:
                    try:
                        payload = json.loads(arguments) if isinstance(arguments, str) else (arguments or {})
                    except (TypeError, ValueError):
                        payload = {}
                    out = test_phase.score_answer(session, idx, payload.get("grid"))
                    if out.get("ok"):
                        per_item.append(bool(out["correct"]))
                        answered = True
                        # Never disclose the verdict: later items are answered on
                        # their own forks, but the model must not learn it here.
                        out = {"ok": True, "recorded": True}
                log["tool_results"].append({"name": name, "result": out})
                outs.append({"type": "function_call_output", "call_id": call_id,
                             "output": json.dumps(out)})
            convo.extend(outs)
            if answered:
                break

        if not answered:
            per_item.append(False)

    return test_phase.finalize(session, per_item)


def run_branched_test_chat(
    client: Any,
    session: ActiveArcTrialSession,
    base_messages: List[Dict[str, Any]],
    *,
    model: str,
    extra_body: Dict[str, Any],
    temperature: float,
    max_turns: int,
    transcript: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Chat-completions equivalent: one branch of *base_messages* per item."""
    from framework.prompting.active_arc_tools import chat_tools_for_phase
    from framework.prompting.response_logging import chat_usage_to_responses_shape

    per_item: List[bool] = []
    tools = chat_tools_for_phase("test", program_mode=False, n_test_items=1)

    for idx in range(len(session.test_items)):
        messages = [dict(m) for m in base_messages]
        messages.append({"role": "user", "content": test_phase.test_item_prompt(session, idx)})
        answered = False

        for turn in range(max_turns):
            kwargs: Dict[str, Any] = {
                "model": model, "messages": messages, "tools": tools,
                "tool_choice": "auto", "temperature": temperature,
            }
            if extra_body:
                kwargs["extra_body"] = extra_body
            raw = client.chat.completions.with_raw_response.create(**kwargs)
            payload = json.loads(raw.text)
            msg = payload["choices"][0]["message"]
            calls = msg.get("tool_calls") or []
            log = {
                "turn": turn, "phase": "test", "test_item": idx,
                "assistant": msg.get("content"),
                "tool_calls": [{"id": c.get("id"),
                                "name": (c.get("function") or {}).get("name"),
                                "arguments": (c.get("function") or {}).get("arguments")}
                               for c in calls],
                "tool_results": [],
                "n_reasoning_details": len(msg.get("reasoning_details") or []),
                "usage": chat_usage_to_responses_shape(payload.get("usage")),
            }
            transcript.append(log)
            # Verbatim, reasoning_details included.
            messages.append(json.loads(json.dumps(msg)))

            if not calls:
                reminder = ("No answer was submitted. Call submit_final_answer with "
                            '{"grid": [[...], ...]} for this test input.')
                log["tool_results"].append(
                    {"name": "_protocol_reminder", "result": {"ok": False, "error": reminder}})
                messages.append({"role": "user", "content": reminder})
                continue

            for c in calls:
                fn = c.get("function") or {}
                name = fn.get("name")
                if name != "submit_final_answer":
                    out = {"ok": False, "error": f"Unknown tool: {name}"}
                else:
                    try:
                        args = json.loads(fn.get("arguments") or "{}")
                    except (TypeError, ValueError):
                        args = {}
                    out = test_phase.score_answer(session, idx, args.get("grid"))
                    if out.get("ok"):
                        per_item.append(bool(out["correct"]))
                        answered = True
                        out = {"ok": True, "recorded": True}
                log["tool_results"].append({"name": name, "result": out})
                messages.append({"role": "tool", "tool_call_id": c.get("id"),
                                 "content": json.dumps(out)})
            if answered:
                break

        if not answered:
            per_item.append(False)

    return test_phase.finalize(session, per_item)
