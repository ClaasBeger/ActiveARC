"""Prompts for Inverse Query Generation teacher and student."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from framework.grids import clone_grid
from framework.inverse_query.session import InverseQuerySession


def _dumps(payload: Any, indent: int = 2) -> str:
    """JSON with grids written one row per line.

    ``json.dumps(indent=2)`` puts every cell on its own line, turning a 13x13
    grid into 170 lines; rows on one line each read like a grid and cost a
    fraction of the tokens.
    """
    def is_grid(v: Any) -> bool:
        return (isinstance(v, list) and v and all(isinstance(r, list) and r and
                all(isinstance(c, int) for c in r) for r in v))

    def render(v: Any, depth: int) -> str:
        pad = " " * (indent * depth)
        inner = " " * (indent * (depth + 1))
        if is_grid(v):
            rows = ",\n".join(inner + json.dumps(r, separators=(",", ":")) for r in v)
            return "[\n" + rows + "\n" + pad + "]"
        if isinstance(v, dict):
            if not v:
                return "{}"
            items = ",\n".join(inner + json.dumps(k) + ": " + render(val, depth + 1) for k, val in v.items())
            return "{\n" + items + "\n" + pad + "}"
        if isinstance(v, list):
            if not v:
                return "[]"
            items = ",\n".join(inner + render(val, depth + 1) for val in v)
            return "[\n" + items + "\n" + pad + "]"
        return json.dumps(v, ensure_ascii=False)

    return render(payload, 0)


def _approx(n: int) -> str:
    """A size the model can weigh before paying for it: 19,710 -> '20,000'."""
    if n < 1_000:
        return str(n)
    step = 1_000 if n < 20_000 else 5_000
    return f"{int(round(n / step) * step):,}"


def _clip(text: Optional[str], limit: int = 80_000) -> Optional[str]:
    if text is None:
        return None
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n\n# ... truncated ({len(text)} chars total)"


def matched_teacher_developer_prompt(session: "InverseQuerySession") -> str:
    """Brief for the matched comparison: choose K demonstrations, nothing else.

    Says what the setting is and what is scored, and stops there. It does not say
    what makes a demonstration useful -- no mention of diversity, coverage, edge
    cases or disambiguating the rule -- because how a rule-aware model chooses is
    the thing being measured, and naming it would measure the prompt instead.
    """
    k = session.max_demonstrations
    # Free variant: how many pairs a rule-aware teacher chooses to show is the
    # measurement, so the count is disclosed as recorded rather than scored --
    # saying it is scored would push the teacher to economise and measure how few
    # it can be pressured into instead.
    if k is None:
        job = ("and one input-output example. Your job is to assemble "
               "demonstration pairs of this rule.")
        seen = ("Those pairs are then given to a separate solver that has never seen "
                "this task. It sees your pairs and nothing else: ")
        scored = ("From them alone it must infer the rule and apply it to held-out "
                  "inputs of this task. You are scored on whether it answers those "
                  "correctly. The number of pairs you show will also be recorded.")
        stop = ("Call finish_teaching to hand the set over and end teaching.")
    else:
        job = ("and one input-output example. Your job is to assemble exactly "
               f"{k} demonstration pairs of this rule.")
        seen = ("Those pairs are then given to a separate solver that has never seen "
                f"this task. It sees your {k} pairs and nothing else: ")
        scored = ("From them alone it must infer the rule and apply it to held-out "
                  "inputs of this task. Whether it answers those correctly is what "
                  "is scored.")
        stop = None
    lines = [
        "You are dealing with grid transformation tasks: an input grid is mapped "
        "to an output grid according to an underlying rule.",
        "Grids are rectangular matrices with integer colors 0-9.",
        "",
        "You are given the rule in words, the verifier program that implements it, "
        + job,
        "",
        seen + "not the rule, not the "
        "verifier program, not the example you were given, and nothing you write in "
        "prose. " + scored,
        "",
        "Use show_transformed_input to add a pair: you author the input and the "
        "environment computes the output. An input the verifier cannot evaluate is "
        "refused and no pair is added; you may submit a different one.",
    ]
    if stop:
        lines.append(stop)
    return "\n".join(lines)


def matched_teacher_exam_message(input_grid: List[List[int]],
                                 index: int, n_items: int) -> str:
    """One held-out item for the teacher to answer before it teaches.

    The teacher is checked on the items the solver will face, so a set produced by
    a teacher that does not have the rule can be told apart from a badly chosen
    one. Its context is reset afterwards: knowing the items while teaching would
    let it demonstrate toward them rather than toward the rule.
    """
    payload = {"item": index + 1, "n_items": n_items, "input": clone_grid(input_grid)}
    return (
        "Before you teach: apply the rule to this input yourself and submit the "
        "output with submit_prediction. This checks that you have the rule; you "
        "will not keep this exchange."
        + "\n\n```json\n" + _dumps(payload) + "\n```"
    )


def teacher_developer_prompt(session: InverseQuerySession) -> str:
    n = session.exam_n
    lines = [
        "You are dealing with grid transformation tasks: an input grid is mapped "
        "to an output grid according to an underlying rule.",
        "Grids are rectangular matrices with integer colors 0–9.",
        "",
        "You are the Teacher in Inverse Query Generation.",
        "You are given one input-output example, the rule in words, and the verifier "
        "program that will grade the exam. A Student has none of these.",
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
        "- Your one example is teacher-only. The Student does not see it unless you show "
        "that pair with show_example or show_transformed_input.",
        # States what the environment does, not what to author. Telling the
        # teacher to mirror the example steers its choice of inputs, which is the
        # very thing this setting measures.
        "- The verifier is only defined for inputs that follow the task's input "
        "conventions. An input it cannot evaluate is refused: no pair is added and the "
        "Student is not shown it, and you may submit a different one.",
        "- The Student never sees the rule or the verifier. Do not try to speak to them "
        "in prose; only the tools above change what they see.",
    ]
    if session.implementation_available():
        src = session.programs.verifier_source or ""
        lines.append(
            "- get_verifier_implementation: the code behind the verifier program's op names, "
            "trimmed to this task (%d lines, about %s characters). Free -- not counted, "
            "not shown to the Student." % (src.count("\n") + 1, _approx(len(src)))
        )
    lines += [
        f"- The trial is scored by how many of the {n} exam items the Student gets right. "
        "The number of show_* and query_student calls is also logged.",
    ]
    return "\n".join(lines)


def _program_payload(source: Optional[str]) -> Any:
    """A verifier source as it should sit in the JSON briefing.

    ConceptARC verifiers are DSL descriptors that are themselves JSON; nesting
    them as objects keeps them readable instead of backslash-escaped strings.
    Everything else is program text and stays a string.
    """
    if not source:
        return None
    text = source.strip()
    if text.startswith("{"):
        try:
            return json.loads(text)
        except ValueError:
            pass
    return _clip(source)


def teacher_task_message(session: InverseQuerySession) -> str:
    programs = session.programs
    if programs.verifier_program_json is not None:
        # The descriptor is short; the interpreter behind its op names is long
        # (hundreds of lines), so it is fetched with get_verifier_implementation
        # rather than pasted into every briefing.
        src = programs.verifier_source or ""
        verifier: Any = {"program": programs.verifier_program_json,
                         "implementation": "available via the get_verifier_implementation tool "
                                           "(%d lines, about %s characters)" % (src.count("\n") + 1, _approx(len(src)))}
    else:
        verifier = _program_payload(programs.verifier_source)
    payload: Dict[str, Any] = {
        "natural_language_rule": programs.nl_rule,
        "verifier_program": verifier,
    }
    missing = [k for k, v in (("natural_language_rule", programs.nl_rule),
                              ("verifier_program", programs.verifier_source)) if not v]
    note = ("\n\nNote: unavailable for this task: " + ", ".join(missing) + ".") if missing else ""
    sample = session.teacher_sample_json()
    if sample is not None:
        sample_block = (
            "\n\nYour one example (teacher-only; the Student has not seen it):\n"
            f"```json\n{_dumps(sample)}\n```"
        )
    else:
        sample_block = "\n\nNo example could be drawn for this task; work from the rule and verifier."
    return (
        "Here is the task (JSON): the rule in words and the verifier program that "
        "grades the exam. Teach the Student, then call start_exam when ready.\n\n"
        f"```json\n{json.dumps(payload, indent=2)}\n```"
        f"{note}"
        f"{sample_block}"
    )


def teacher_exam_message(session: InverseQuerySession, input_grid: List[List[int]], exam_index: int) -> str:
    """One exam item for the teacher's own sanity check, before any teaching."""
    payload = {"exam_item": exam_index, "exam_n": session.exam_n, "input": clone_grid(input_grid)}
    return (
        "Sanity check before you teach: solve this exam item yourself, using the rule, "
        "the verifier and your example above. The Student will face the same items "
        "later. Submit with submit_prediction; do not paste grids as plain text."
        + (" You may call get_verifier_implementation first if a convention is unclear."
           if session.implementation_available() else "")
        + "\n\n"
        f"```json\n{_dumps(payload)}\n```"
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
    return f"{lead}\n\n```json\n{_dumps(payload)}\n```"
