"""Prompts for Inverse Query Generation teacher and student."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from framework.grids import clone_grid
from framework.inverse_query.session import InverseQuerySession


def _clip(text: Optional[str], limit: int = 80_000) -> Optional[str]:
    if text is None:
        return None
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n\n# ... truncated ({len(text)} chars total)"


def teacher_developer_prompt(session: InverseQuerySession) -> str:
    n = session.exam_n
    lines = [
        "You are dealing with grid transformation tasks: an input grid is mapped "
        "to an output grid according to an underlying rule.",
        "Grids are rectangular matrices with integer colors 0–9.",
        "",
        "You are the Teacher in Inverse Query Generation.",
        "You know the rule. A Student does not.",
        "Your job is to teach the Student using demonstrations and optional probes, "
        "then send them to an exam.",
        "",
        "Rules:",
        "- show_example: you author both input and output. If it matches the rule, "
        "the Student is shown the pair and you only get a success acknowledgement. "
        "If it does not match, the Student does not see it and you receive the gold output.",
        "- show_transformed_input: you author only the input; the environment fills "
        "the gold output and shows the pair to the Student.",
        "- query_student: the Student predicts an output for your input. You see their "
        "answer vs gold. They do NOT see gold unless you later show that pair with "
        "show_example or show_transformed_input.",
        f"- start_exam: the Student then answers {n} held-out generator inputs one at a "
        "time, with no feedback, using only the demonstrations you have shown.",
        "- You may receive one teacher-only generator sample. The Student does not see it "
        "unless you later show that pair with show_example or show_transformed_input.",
        "- The Student never sees these programs. Do not try to speak to them in prose; "
        "only the tools above change what they see.",
        f"- The trial is scored by how many of the {n} exam items the Student gets right. "
        "The number of show_* and query_student calls is also logged.",
    ]
    return "\n".join(lines)


def teacher_task_message(session: InverseQuerySession) -> str:
    programs = session.programs
    payload: Dict[str, Any] = {
        "verifier_slot": programs.verifier_slot,
        "generator_label": programs.generator_label,
        "verifier_label": programs.verifier_label,
        "natural_language_rule": programs.nl_rule,
        "generator_program": _clip(programs.generator_source),
        "verifier_program": _clip(programs.verifier_source),
    }
    missing = []
    if not programs.generator_source:
        missing.append("generator_program")
    if not programs.verifier_source:
        missing.append("verifier_program")
    if not programs.nl_rule:
        missing.append("natural_language_rule")
    note = ""
    if missing:
        note = (
            "\n\nNote: these fields are unavailable for this task: "
            + ", ".join(missing)
            + "."
        )
    sample_block = ""
    sample = session.teacher_sample_json()
    if sample is not None:
        compact = json.dumps(sample, separators=(",", ":"))
        sample_block = (
            "\n\nTeacher-only generator sample (not shown to the Student; "
            "do not assume they have seen it). Compact JSON:\n"
            f"```json\n{compact}\n```"
        )
    return (
        "Here are the programs for this task (JSON). Teach the Student, then call "
        "start_exam when ready.\n"
        "ARC-GEN generators use ordinary Python helpers from common.py (included "
        "when referenced). RE-ARC verifiers use the Michael Hodel DSL; only the "
        "primitives this verifier calls are included. Prefer the generator and "
        "verifier together over golfed one-liners.\n\n"
        f"```json\n{json.dumps(payload, indent=2)}\n```"
        f"{note}"
        f"{sample_block}"
    )


def student_developer_prompt() -> str:
    return "\n".join(
        [
            "You are solving a grid transformation task.",
            "Grids use integer values 0-9 to represent color.",
            "You will be shown zero or more input-output demonstration pairs.",
            "Infer the transformation rule from those pairs only.",
            "When given an input grid, submit your predicted output with submit_prediction.",
            "Do not paste grids as plain text.",
        ]
    )


def student_task_message(
    session: InverseQuerySession,
    input_grid: List[List[int]],
    *,
    kind: str,
    exam_index: Optional[int] = None,
) -> str:
    payload: Dict[str, Any] = {
        "demonstrations": session.demonstrations_json(),
        "input": clone_grid(input_grid),
    }
    if kind == "exam":
        payload["exam_item"] = exam_index
        payload["exam_n"] = session.exam_n
        lead = (
            "Exam. Predict the output for input. You will not be told whether "
            "you are correct. Use submit_prediction."
        )
    else:
        lead = (
            "Predict the output for input given the demonstrations. "
            "Use submit_prediction."
        )
    return f"{lead}\n\n```json\n{json.dumps(payload, indent=2)}\n```"
