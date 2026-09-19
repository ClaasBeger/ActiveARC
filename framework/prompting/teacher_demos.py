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

from framework.inverse_query.prompts import (
    matched_teacher_developer_prompt,
    matched_teacher_exam_message,
    teacher_task_message,
)
from framework.inverse_query.session import InverseQuerySession
from framework.inverse_query.tools import (
    STUDENT_TOOLS,
    execute_teacher_tool,
    parse_student_prediction,
    teacher_tools_for,
)
from framework.grids import is_equal_grid
from framework.prompting.clients import (
    PROVIDER_OPENAI,
    ResponsesConversation,
    build_client,
    resolve_model,
    resolve_provider,
    resolve_store,
    responses_extras,
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



def run_teacher_exam(
    client: Any,
    session: InverseQuerySession,
    items: List[tuple],
    *,
    model: str,
    provider: str,
    reasoning_effort: Optional[str],
    store: bool,
    max_turns: int = 6,
) -> Dict[str, Any]:
    """Have the teacher answer the solver's own held-out items, before teaching.

    Each item gets its own context, and none of it survives into the teaching
    phase: a teacher that remembered these would demonstrate toward them rather
    than toward the rule, which is teaching to the test rather than teaching.

    A teacher that fails here did not have the rule, so its demonstrations say
    nothing about how a rule-aware model chooses -- those trials want reporting
    apart from the rest rather than averaging in.
    """
    results: List[Dict[str, Any]] = []
    transcripts: List[Dict[str, Any]] = []
    for idx, (test_input, gold) in enumerate(items):
        convo = ResponsesConversation(provider, [
            {"role": "developer", "content": matched_teacher_developer_prompt(session)},
            {"role": "user", "content": teacher_task_message(session)},
            {"role": "user", "content": matched_teacher_exam_message(test_input, idx, len(items))},
        ])
        prediction = None
        for turn in range(max_turns):
            kwargs: Dict[str, Any] = {
                "model": model, "tools": STUDENT_TOOLS, "store": store,
                **convo.create_kwargs(),
            }
            kwargs.update(responses_extras(provider, model, reasoning_effort))
            response = client.responses.create(**kwargs)
            calls = [i for i in (getattr(response, "output", None) or [])
                     if _item_type(i) == "function_call"]
            transcripts.append({"item": idx, "turn": turn,
                                "response": summarize_response(response),
                                "assistant": _assistant_text(response)})
            convo.record_turn(response, [_call_fields(c) for c in calls],
                              assistant_text=_assistant_text(response))
            if not calls:
                convo.extend([{"role": "user", "content":
                               "Submit the output grid with submit_prediction."}])
                continue
            outs = []
            done = False
            for c in calls:
                call_id, name, arguments = _call_fields(c)
                parsed = parse_student_prediction(arguments) if name == "submit_prediction" \
                    else {"ok": False, "error": f"Unknown tool: {name}"}
                if parsed.get("ok"):
                    prediction = parsed["grid"]
                    done = True
                    parsed = {"ok": True, "recorded": True}
                outs.append({"type": "function_call_output", "call_id": call_id,
                             "output": json.dumps(parsed)})
            convo.extend(outs)
            if done:
                break
        correct = prediction is not None and is_equal_grid(prediction, gold)
        results.append({"item": idx, "correct": bool(correct),
                        "answered": prediction is not None})
    passed = bool(results) and all(r["correct"] for r in results)
    return {"items": results, "n_correct": sum(1 for r in results if r["correct"]),
            "n_items": len(results), "passed": passed, "transcript": transcripts}


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
        {"role": "developer", "content": matched_teacher_developer_prompt(session)},
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
        kwargs.update(
            responses_extras(resolved_provider, resolved_model, reasoning_effort)
        )
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
            # Unbudgeted teaching has no count to reach, so a turn with no tool
            # call is the teacher saying it is done. Prodding it instead would
            # leave it no way to stop short of max_turns.
            if target is None:
                if session.demonstrations:
                    reason = "teacher_stopped"
                    break
                reminder = (
                    "No demonstrations shown yet. Use show_transformed_input; "
                    "text alone reaches no one."
                )
                log["tool_results"].append(
                    {"name": "_protocol_reminder", "result": {"ok": False, "error": reminder}})
                convo.extend([{"role": "user", "content": reminder}])
                continue
            remaining = target - len(session.demonstrations)
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
