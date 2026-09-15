"""JSON trial records for Inverse Query Generation."""

from __future__ import annotations

from typing import Any, Dict, List

from framework.grids import clone_grid
from framework.inverse_query.session import InverseQuerySession


def build_inverse_query_record(
    session: InverseQuerySession,
    result: Dict[str, Any],
) -> Dict[str, Any]:
    score = session.exam_score()
    exam_items: List[Dict[str, Any]] = []
    for i, pair in enumerate(session.exam_pairs):
        pred = session.exam_predictions[i] if i < len(session.exam_predictions) else None
        exam_items.append(
            {
                "input": clone_grid(pair.input),
                "gold_output": clone_grid(pair.output),
                "prediction": clone_grid(pred) if pred is not None else None,
                "correct": session.exam_correct[i] if i < len(session.exam_correct) else None,
            }
        )
    programs = session.programs
    return {
        "setting": "inverse_query",
        "task_id": session.task_id,
        "seed": session.seed,
        "dataset": session.dataset,
        "backend": result.get("backend"),
        "model": result.get("model"),
        "teacher_model": result.get("teacher_model"),
        "student_model": result.get("student_model"),
        "reasoning_effort": result.get("reasoning_effort"),
        "exam_n": session.exam_n,
        "n_show_example": session.n_show_example,
        "n_show_transformed": session.n_show_transformed,
        "n_show_pair": session.n_show_example + session.n_show_transformed,
        "n_query_student": session.n_query_student,
        "n_failed_show": session.n_failed_show,
        "n_get_implementation": session.n_get_implementation,
        "n_demonstrations": len(session.demonstrations),
        "exam_correct": score["exam_correct"],
        "exam_score": score["exam_score"],
        "correct": score["exam_score"] == 1.0 if score["exam_score"] is not None else None,
        "phase": session.phase,
        # Top level as well, so the run audits that key on verifier_slot see it.
        "verifier_slot": programs.verifier_slot,
        "programs": {
            "verifier_slot": programs.verifier_slot,
            "verifier_label": programs.verifier_label,
            "verifier_kind": programs.verifier_kind,
            "has_verifier_source": bool(programs.verifier_source),
            "nl_rule": programs.nl_rule,
            "nl_rule_source": programs.nl_rule_source,
        },
        "teacher_check": {
            "ran": session.exam_predrawn,
            "passed": session.teacher_exam_passed,
            "n_correct": sum(1 for v in session.teacher_exam_correct if v),
            "per_item": list(session.teacher_exam_correct),
            "predictions": [clone_grid(p) if p is not None else None
                            for p in session.teacher_exam_predictions],
            "exam_items_replaced_after_check": session.exam_replaced,
        },
        "include_teacher_sample": session.include_teacher_sample,
        "teacher_sample": session.teacher_sample_json(),
        "demonstrations": session.demonstrations_json(),
        "probes": session.probes,
        "exam": exam_items,
        "final": result.get("final"),
        "usage": result.get("usage"),
        "teacher_transcript": result.get("teacher_transcript"),
        "student_transcript": result.get("student_transcript"),
        "teacher_check_transcript": result.get("teacher_check_transcript"),
    }
