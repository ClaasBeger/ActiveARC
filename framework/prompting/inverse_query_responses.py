"""OpenAI Responses API loop for Inverse Query Generation (teacher + student)."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from framework.inverse_query.prompts import (
    student_developer_prompt,
    student_task_message,
    teacher_developer_prompt,
    teacher_task_message,
)
from framework.inverse_query.session import InverseQuerySession
from framework.inverse_query.tools import (
    STUDENT_TOOLS,
    TEACHER_TOOLS,
    execute_teacher_tool,
    parse_student_prediction,
)
from framework.prompting.active_arc_tools import DEFAULT_OPENAI_MODEL, looks_like_raw_grid
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


def _student_plain_text_reminder(assistant_text: Optional[str]) -> Optional[str]:
    if not looks_like_raw_grid(assistant_text):
        return None
    return (
        "Do not paste grids as plain text. Call submit_prediction with "
        '{"grid": [[...], ...]}.'
    )


def _run_student_prediction(
    client: Any,
    session: InverseQuerySession,
    input_grid: List[List[int]],
    *,
    model: str,
    reasoning_effort: Optional[str],
    store: bool,
    max_turns: int,
    kind: str,
    exam_index: Optional[int],
) -> Dict[str, Any]:
    """One student prediction (probe or exam item). Rebuilds context each call."""
    transcript: List[Dict[str, Any]] = []
    pending_input: List[Any] = [
        {"role": "developer", "content": student_developer_prompt()},
        {
            "role": "user",
            "content": student_task_message(
                session, input_grid, kind=kind, exam_index=exam_index
            ),
        },
    ]
    previous_response_id: Optional[str] = None
    prediction: Optional[List[List[int]]] = None
    stop_reason = "max_turns"

    for turn in range(max_turns):
        create_kwargs: Dict[str, Any] = {
            "model": model,
            "tools": STUDENT_TOOLS,
            "input": pending_input,
            "store": store,
        }
        if reasoning_effort is not None:
            create_kwargs["reasoning"] = {"effort": reasoning_effort}
        if previous_response_id is not None:
            create_kwargs["previous_response_id"] = previous_response_id
        response = client.responses.create(**create_kwargs)
        previous_response_id = response.id
        function_calls = [
            item
            for item in (getattr(response, "output", None) or [])
            if _output_item_type(item) == "function_call"
        ]
        turn_log = {
            "turn": turn,
            "response_id": response.id,
            "response": summarize_response(response),
            "assistant": _assistant_text(response),
            "tool_calls": [
                {
                    "call_id": _function_call_fields(c)[0],
                    "name": _function_call_fields(c)[1],
                    "arguments": _function_call_fields(c)[2],
                }
                for c in function_calls
            ],
            "tool_results": [],
        }
        transcript.append(turn_log)

        if not function_calls:
            reminder = _student_plain_text_reminder(_assistant_text(response))
            if reminder is not None:
                turn_log["tool_results"].append(
                    {"name": "_protocol_reminder", "result": {"ok": False, "error": reminder}}
                )
                pending_input = [{"role": "user", "content": reminder}]
                continue
            stop_reason = "model_stop"
            break

        pending_input = []
        submitted = False
        for item in function_calls:
            call_id, name, arguments = _function_call_fields(item)
            if name != "submit_prediction":
                out = {"ok": False, "error": f"Unknown tool: {name}"}
            else:
                parsed = parse_student_prediction(arguments)
                if parsed.get("ok"):
                    prediction = parsed["grid"]
                    out = {"ok": True, "recorded": True}
                    submitted = True
                else:
                    out = parsed
            turn_log["tool_results"].append({"name": name, "result": out})
            pending_input.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(out),
                }
            )
        if submitted:
            stop_reason = "submitted"
            break

    return {
        "prediction": prediction,
        "reason": stop_reason,
        "transcript": transcript,
        "usage": usage_totals(transcript),
    }


def run_inverse_query_responses_loop(
    session: InverseQuerySession,
    *,
    model: Optional[str] = None,
    max_turns: int = 64,
    student_max_turns: int = 8,
    reasoning_effort: Optional[str] = "low",
    store: bool = True,
) -> Dict[str, Any]:
    """Teacher loop, then sequential student exam."""
    try:
        from openai import OpenAI
    except ImportError as e:
        raise ImportError("Install the OpenAI SDK: pip install openai") from e

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY in the environment.")

    resolved_model = model or os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    client = OpenAI(api_key=api_key)

    teacher_transcript: List[Dict[str, Any]] = []
    student_transcript: List[Dict[str, Any]] = []
    last_result: Dict[str, Any] = {
        "session": session,
        "backend": "responses",
        "model": resolved_model,
        "reasoning_effort": reasoning_effort,
        "teacher_transcript": teacher_transcript,
        "student_transcript": student_transcript,
        "final": None,
        "usage": None,
    }

    previous_response_id: Optional[str] = None
    pending_input: List[Any] = [
        {"role": "developer", "content": teacher_developer_prompt(session)},
        {"role": "user", "content": teacher_task_message(session)},
    ]

    exam_started = False
    teacher_stop_reason = "max_turns"

    for turn in range(max_turns):
        if session.phase != "teach":
            break
        create_kwargs: Dict[str, Any] = {
            "model": resolved_model,
            "tools": TEACHER_TOOLS,
            "input": pending_input,
            "store": store,
        }
        if reasoning_effort is not None:
            create_kwargs["reasoning"] = {"effort": reasoning_effort}
        if previous_response_id is not None:
            create_kwargs["previous_response_id"] = previous_response_id
        response = client.responses.create(**create_kwargs)
        previous_response_id = response.id
        function_calls = [
            item
            for item in (getattr(response, "output", None) or [])
            if _output_item_type(item) == "function_call"
        ]
        turn_log = {
            "turn": turn,
            "phase": session.phase,
            "response_id": response.id,
            "response": summarize_response(response),
            "assistant": _assistant_text(response),
            "tool_calls": [
                {
                    "call_id": _function_call_fields(c)[0],
                    "name": _function_call_fields(c)[1],
                    "arguments": _function_call_fields(c)[2],
                }
                for c in function_calls
            ],
            "tool_results": [],
        }
        teacher_transcript.append(turn_log)

        if not function_calls:
            teacher_stop_reason = "teacher_stop"
            last_result["final"] = {
                "reason": "teacher_stop",
                "message": _assistant_text(response),
                "phase": session.phase,
            }
            last_result["usage"] = usage_totals(
                teacher_transcript + _flatten_student_turns(student_transcript)
            )
            return last_result

        pending_input = []
        for item in function_calls:
            call_id, name, arguments = _function_call_fields(item)
            out = execute_teacher_tool(session, name, arguments)

            if out.get("delegate") == "query_student":
                student_run = _run_student_prediction(
                    client,
                    session,
                    out["input"],
                    model=resolved_model,
                    reasoning_effort=reasoning_effort,
                    store=store,
                    max_turns=student_max_turns,
                    kind="probe",
                    exam_index=None,
                )
                student_transcript.append(
                    {
                        "kind": "probe",
                        "input": out["input"],
                        **student_run,
                    }
                )
                out = session.record_probe(
                    out["input"], student_run.get("prediction"), out["gold"]
                )

            turn_log["tool_results"].append({"name": name, "result": out})

            if name == "start_exam" and out.get("ok"):
                exam_started = True
                pending_input.append(
                    {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": json.dumps(
                            {k: v for k, v in out.items() if k != "first_test_input"}
                        ),
                    }
                )
                break

            pending_input.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(out),
                }
            )
        if exam_started:
            break

    if not exam_started:
        last_result["final"] = {
            "reason": teacher_stop_reason,
            "phase": session.phase,
            "n_show_pair": session.n_show_example + session.n_show_transformed,
            "n_query_student": session.n_query_student,
        }
        last_result["usage"] = usage_totals(
            teacher_transcript + _flatten_student_turns(student_transcript)
        )
        return last_result

    for i in range(session.exam_n):
        if session.phase != "exam":
            break
        exam_input = session.current_exam_input()
        if exam_input is None:
            break
        student_run = _run_student_prediction(
            client,
            session,
            exam_input,
            model=resolved_model,
            reasoning_effort=reasoning_effort,
            store=store,
            max_turns=student_max_turns,
            kind="exam",
            exam_index=i + 1,
        )
        student_transcript.append(
            {
                "kind": "exam",
                "exam_index": i + 1,
                "input": exam_input,
                **student_run,
            }
        )
        pred = student_run.get("prediction")
        if pred is None:
            session.mark_exam_unanswered()
        else:
            session.submit_exam_answer(pred)

    score = session.exam_score()
    last_result["final"] = {
        "reason": "exam_complete" if session.phase == "done" else "exam_incomplete",
        "phase": session.phase,
        **score,
        "n_show_pair": session.n_show_example + session.n_show_transformed,
        "n_query_student": session.n_query_student,
    }
    last_result["usage"] = usage_totals(
        teacher_transcript + _flatten_student_turns(student_transcript)
    )
    return last_result


def _flatten_student_turns(student_transcript: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for block in student_transcript:
        for turn in block.get("transcript") or []:
            out.append(turn)
    return out
