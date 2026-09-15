#!/usr/bin/env python3
"""Run one Inverse Query Generation trial (teacher + student).

Example::

    python -m pipelines.run_inverse_query_agent --dataset parc --task-id test2_t1 --seed 0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from framework.inverse_query.records import build_inverse_query_record
from framework.inverse_query.session import create_inverse_query_session
from framework.prompting.active_arc_tools import DEFAULT_OPENAI_MODEL
from framework.prompting.inverse_query_responses import run_inverse_query_responses_loop


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Inverse Query Generation (teacher + student)")
    p.add_argument("--task-id", type=str, default=None)
    p.add_argument(
        "--dataset",
        choices=["arc", "arc2", "conceptarc", "parc"],
        default="arc",
        help="Task pool (same ids as the Luna eval batches).",
    )
    p.add_argument("--seed", type=int, default=0)
    p.add_argument(
        "--exam-n",
        type=int,
        default=10,
        help="Held-out exam items sampled from the generator (default 10).",
    )
    p.add_argument(
        "--model",
        type=str,
        default=None,
        help=f"OpenAI model name (default: env OPENAI_MODEL or {DEFAULT_OPENAI_MODEL}).",
    )
    p.add_argument("--teacher-model", type=str, default=None, help="Teacher model (default: --model).")
    p.add_argument("--student-model", type=str, default=None, help="Student model (default: --model).")
    p.add_argument("--teacher-check", action=argparse.BooleanOptionalAction, default=False,
                   help="Teacher must solve the pre-drawn exam before teaching.")
    p.add_argument("--max-turns", type=int, default=64, help="Teacher tool-loop budget.")
    p.add_argument(
        "--student-max-turns",
        type=int,
        default=8,
        help="Student tool-loop budget per probe or exam item.",
    )
    p.add_argument("--reasoning-effort", type=str, default="low")
    p.add_argument(
        "--teacher-sample",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Give the teacher one compact generator sample (not shown to the student). Default: on.",
    )
    p.add_argument("--dump-transcript", type=str, default=None)
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    session = create_inverse_query_session(
        seed=args.seed,
        task_id=args.task_id,
        dataset=args.dataset,
        exam_n=args.exam_n,
        include_teacher_sample=args.teacher_sample,
    )
    reasoning_effort = None if args.reasoning_effort.lower() == "none" else args.reasoning_effort
    result = run_inverse_query_responses_loop(
        session,
        model=args.model,
        teacher_model=args.teacher_model,
        student_model=args.student_model,
        teacher_check=args.teacher_check,
        max_turns=args.max_turns,
        student_max_turns=args.student_max_turns,
        reasoning_effort=reasoning_effort,
    )
    out = build_inverse_query_record(session, result)
    text = json.dumps(out, indent=2)
    print(text)
    if args.dump_transcript:
        Path(args.dump_transcript).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
