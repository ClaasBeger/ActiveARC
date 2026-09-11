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
        "reasoning_effort": result.get("reasoning_effort"),
        "exam_n": session.exam_n,
        "n_show_example": session.n_show_example,
        "n_show_transformed": session.n_show_transformed,
        "n_show_pair": session.n_show_example + session.n_show_transformed,
        "n_query_student": session.n_query_student,
        "n_failed_show": session.n_failed_show,
        "n_demonstrations": len(session.demonstrations),
        "exam_correct": score["exam_correct"],
        "exam_score": score["exam_score"],
        "correct": score["exam_score"] == 1.0 if score["exam_score"] is not None else None,
        "phase": session.phase,
        "programs": {
            "verifier_slot": programs.verifier_slot,
            "generator_label": programs.generator_label,
            "verifier_label": programs.verifier_label,
            "nl_rule": programs.nl_rule,
            "has_generator_source": bool(programs.generator_source),
            "has_verifier_source": bool(programs.verifier_source),
            "generator_kind": programs.generator_kind,
            "verifier_kind": programs.verifier_kind,
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
    }
