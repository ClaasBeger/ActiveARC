"""OpenAI Responses API loop for Inverse Query Generation (teacher + student)."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from framework.inverse_query.prompts import (
    student_developer_prompt,
    student_task_message,
    teacher_exam_message,
    teacher_developer_prompt,
    teacher_task_message,
)
from framework.inverse_query.session import InverseQuerySession
from framework.inverse_query.tools import (
    STUDENT_TOOLS,
    TEACHER_TOOLS,
    execute_teacher_tool,
    parse_student_prediction,
    teacher_check_tools_for,
    teacher_tools_for,
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


def _student_plain_text_reminder(assistant_text: Optional[str]) -> str:
    """What to say when a turn produced no submit_prediction call.

    A turn can come back with nothing but a reasoning item -- no message, no
    tool call -- and ``status: completed``. That is not an answer, and it is
    not a decision to stop either, so every such turn gets a nudge and another
    go; only the turn budget ends a prediction loop.
    """
    if looks_like_raw_grid(assistant_text):
        return (
            "Do not paste grids as plain text. Call submit_prediction with "
            '{"grid": [[...], ...]}.'
        )
    return (
        "No prediction was submitted. Call submit_prediction with "
        '{"grid": [[...], ...]} for the input above.'
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
    opening: List[Any] = [
        {"role": "developer", "content": student_developer_prompt()},
        {
            "role": "user",
            "content": student_task_message(
                session, input_grid, kind=kind, exam_index=exam_index
            ),
        },
    ]
    return _run_prediction(client, opening, model=model, reasoning_effort=reasoning_effort,
                           store=store, max_turns=max_turns)


def _run_teacher_check_item(
    client: Any,
    session: InverseQuerySession,
    input_grid: List[List[int]],
    *,
    exam_index: int,
    model: str,
    reasoning_effort: Optional[str],
    store: bool,
    max_turns: int,
) -> Dict[str, Any]:
    """The teacher solves one exam item from its normal briefing, fresh context per item."""
    opening: List[Any] = [
        {"role": "developer", "content": teacher_developer_prompt(session)},
        {"role": "user", "content": teacher_task_message(session)},
        {"role": "user", "content": teacher_exam_message(session, input_grid, exam_index)},
    ]
    return _run_prediction(client, opening, model=model, reasoning_effort=reasoning_effort,
                           store=store, max_turns=max_turns,
                           tools=teacher_check_tools_for(session), session=session)


def _run_prediction(
    client: Any,
    pending_input: List[Any],
    *,
    model: str,
    reasoning_effort: Optional[str],
    store: bool,
    max_turns: int,
    tools: Optional[List[Dict[str, Any]]] = None,
    session: Optional[InverseQuerySession] = None,
) -> Dict[str, Any]:
    """Drive one submit_prediction tool loop to a single grid.

    *tools* defaults to the student's; the teacher's sanity check adds the
    implementation lookup, answered here from *session*.
    """
    tools = tools if tools is not None else STUDENT_TOOLS
    transcript: List[Dict[str, Any]] = []
    previous_response_id: Optional[str] = None
    prediction: Optional[List[List[int]]] = None
    stop_reason = "max_turns"

    for turn in range(max_turns):
        create_kwargs: Dict[str, Any] = {
            "model": model,
            "tools": tools,
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
            turn_log["tool_results"].append(
                {"name": "_protocol_reminder", "result": {"ok": False, "error": reminder}}
            )
            pending_input = [{"role": "user", "content": reminder}]
            continue

        pending_input = []
        submitted = False
        for item in function_calls:
            call_id, name, arguments = _function_call_fields(item)
            if name == "get_verifier_implementation" and session is not None:
                out = session.get_verifier_implementation()
            elif name != "submit_prediction":
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
    teacher_model: Optional[str] = None,
    student_model: Optional[str] = None,
    teacher_check: bool = False,
) -> Dict[str, Any]:
    """Optional teacher sanity check, then teacher loop, then sequential student exam.

    *teacher_model* / *student_model* default to *model*. With *teacher_check*
    the exam is drawn first and the teacher must solve every item from its own
    briefing; a trial whose teacher cannot is recorded and stopped before any
    teaching, since a student cannot be taught a rule the teacher cannot apply.
    """
    try:
        from openai import OpenAI
    except ImportError as e:
        raise ImportError("Install the OpenAI SDK: pip install openai") from e

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY in the environment.")

    resolved_model = model or os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    resolved_teacher = teacher_model or resolved_model
    resolved_student = student_model or resolved_model
    client = OpenAI(api_key=api_key)

    teacher_transcript: List[Dict[str, Any]] = []
    student_transcript: List[Dict[str, Any]] = []
    teacher_check_transcript: List[Dict[str, Any]] = []
    last_result: Dict[str, Any] = {
        "session": session,
        "backend": "responses",
        "model": resolved_teacher,
        "teacher_model": resolved_teacher,
        "student_model": resolved_student,
        "reasoning_effort": reasoning_effort,
        "teacher_transcript": teacher_transcript,
        "student_transcript": student_transcript,
        "teacher_check_transcript": teacher_check_transcript,
        "final": None,
        "usage": None,
    }

    def _usage() -> Dict[str, Any]:
        return usage_totals(
            teacher_transcript
            + _flatten_student_turns(student_transcript)
            + _flatten_student_turns(teacher_check_transcript)
        )

    if teacher_check:
        drawn = session.predraw_exam()
        if not drawn.get("ok"):
            last_result["final"] = {"reason": "sampler_exhausted", "phase": session.phase, **drawn}
            last_result["usage"] = _usage()
            return last_result
        predictions: List[Optional[List[List[int]]]] = []
        for i, pair in enumerate(session.exam_pairs):
            run = _run_teacher_check_item(
                client, session, pair.input, exam_index=i + 1, model=resolved_teacher,
                reasoning_effort=reasoning_effort, store=store, max_turns=student_max_turns,
            )
            teacher_check_transcript.append({"kind": "teacher_check", "exam_index": i + 1,
                                             "input": pair.input, **run})
            predictions.append(run.get("prediction"))
        check = session.record_teacher_exam(predictions)
        if not check["passed"]:
            last_result["final"] = {
                "reason": "teacher_failed_check",
                "phase": session.phase,
                "teacher_check": check,
            }
            last_result["usage"] = _usage()
            return last_result

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
            "model": resolved_teacher,
            "tools": teacher_tools_for(session),
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
            # Prose, or a reasoning-only turn with no message at all: neither is
            # a decision to end the trial (start_exam is), so nudge and continue.
            # Only the turn budget ends teaching without an exam.
            reminder = (
                "No tool was called. Teach with show_example / show_transformed_input / "
                "query_student, or call start_exam when you are done. Text alone reaches no one."
            )
            turn_log["tool_results"].append(
                {"name": "_protocol_reminder", "result": {"ok": False, "error": reminder}}
            )
            pending_input = [{"role": "user", "content": reminder}]
            continue

        pending_input = []
        for item in function_calls:
            call_id, name, arguments = _function_call_fields(item)
            out = execute_teacher_tool(session, name, arguments)

            if out.get("delegate") == "query_student":
                student_run = _run_student_prediction(
                    client,
                    session,
                    out["input"],
                    model=resolved_student,
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
        last_result["usage"] = _usage()
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
            model=resolved_student,
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
    last_result["usage"] = _usage()
    return last_result


def _flatten_student_turns(student_transcript: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for block in student_transcript:
        for turn in block.get("transcript") or []:
            out.append(turn)
    return out
