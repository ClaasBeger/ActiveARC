"""Collect a teacher's K demonstrations, and nothing else.

The matched comparison needs the teaching set, not a verdict on it: the set is
scored afterwards by the same evaluator that scores the authored one, so this
loop stops as soon as K demonstrations exist. There is no exam here, and no
student -- a teacher that could interrogate a particular learner would hold
information the ARC author who wrote the authored demos never had.

What varies between this and the static arm is only who chose the pairs. Both
end with K of them for the same task, and both are answered by the same model on
the same held-out items.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from framework.inverse_query.prompts import teacher_developer_prompt, teacher_task_message
from framework.inverse_query.session import InverseQuerySession
from framework.inverse_query.tools import execute_teacher_tool, teacher_tools_for
from framework.prompting.clients import (
    PROVIDER_OPENAI,
    ResponsesConversation,
    build_client,
    resolve_model,
    resolve_provider,
    resolve_store,
)
from framework.prompting.response_logging import summarize_response, usage_totals


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


def collect_teacher_demos(
    session: InverseQuerySession,
    *,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    reasoning_effort: Optional[str] = "low",
    max_turns: int = 32,
    store: bool = True,
) -> Dict[str, Any]:
    """Drive the teacher until it has shown ``session.max_demonstrations`` pairs."""
    resolved_provider = resolve_provider(provider, model)
    resolved_model = resolve_model(resolved_provider, model)
    client = build_client(resolved_provider)
    store = resolve_store(resolved_provider, store)

    convo = ResponsesConversation(resolved_provider, [
        {"role": "developer", "content": teacher_developer_prompt(session)},
        {"role": "user", "content": teacher_task_message(session)},
    ])
    transcript: List[Dict[str, Any]] = []
    target = session.max_demonstrations
    reason = "max_turns"

    for turn in range(max_turns):
        if target is not None and len(session.demonstrations) >= target:
            reason = "demos_complete"
            break
        kwargs: Dict[str, Any] = {
            "model": resolved_model,
            "tools": teacher_tools_for(session),
            "store": store,
            **convo.create_kwargs(),
        }
        if reasoning_effort is not None:
            kwargs["reasoning"] = {"effort": reasoning_effort}
        response = client.responses.create(**kwargs)
        calls = [i for i in (getattr(response, "output", None) or [])
                 if _item_type(i) == "function_call"]
        log = {
            "turn": turn,
            "response_id": getattr(response, "id", None),
            "response": summarize_response(response),
            "assistant": _assistant_text(response),
            "tool_calls": [dict(zip(("call_id", "name", "arguments"), _call_fields(c)))
                           for c in calls],
            "tool_results": [],
            "n_demonstrations": len(session.demonstrations),
        }
        transcript.append(log)
        convo.record_turn(response, [_call_fields(c) for c in calls],
                          assistant_text=_assistant_text(response))

        if not calls:
            remaining = (target - len(session.demonstrations)) if target else 1
            reminder = (
                f"{remaining} more demonstration(s) needed. Use show_example or "
                "show_transformed_input; text alone reaches no one."
            )
            log["tool_results"].append(
                {"name": "_protocol_reminder", "result": {"ok": False, "error": reminder}})
            convo.extend([{"role": "user", "content": reminder}])
            continue

        outs = []
        for c in calls:
            call_id, name, arguments = _call_fields(c)
            if name == "start_exam":
                # No exam in this setting; the set is scored elsewhere.
                remaining = (target - len(session.demonstrations)) if target else 0
                out = {"ok": False, "error": (
                    f"There is no exam here. Show {remaining} more demonstration(s); "
                    "the set is complete after that.")} if remaining > 0 else {
                    "ok": True, "message": "The teaching set is complete."}
            else:
                out = execute_teacher_tool(session, name, arguments)
                if out.get("delegate") == "query_student":
                    out = {"ok": False,
                           "error": "Probing the student is not available in this setting."}
            log["tool_results"].append({"name": name, "result": out})
            outs.append({"type": "function_call_output", "call_id": call_id,
                         "output": json.dumps(out)})
        convo.extend(outs)

    if target is not None and len(session.demonstrations) >= target:
        reason = "demos_complete"

    return {
        "provider": resolved_provider,
        "model": resolved_model,
        "reasoning_effort": reasoning_effort,
        "reason": reason,
        "n_demonstrations": len(session.demonstrations),
        "target": target,
        "demonstrations": session.demonstrations_json(),
        "n_show_example": session.n_show_example,
        "n_show_transformed": session.n_show_transformed,
        "n_failed_show": session.n_failed_show,
        "transcript": transcript,
        "usage": usage_totals(transcript),
    }
