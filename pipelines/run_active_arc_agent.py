#!/usr/bin/env python3
"""Run an OpenAI tool-calling agent on one ActiveARC trial (same rules as the Streamlit UI).

Requires ``OPENAI_API_KEY``. Default backend is the Responses API with ``gpt-5.6-luna``.

Example::

    python -m pipelines.run_active_arc_agent --task-id 8eb1be9a --seed 42

    # Legacy Chat Completions backend:
    python -m pipelines.run_active_arc_agent --backend chat --model gpt-4o

"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from framework.active_arc.headless_trial import create_trial_session
from framework.active_arc.trial_record import build_trial_record
from framework.prompting.active_arc_openai import run_openai_agent_loop
from framework.prompting.active_arc_responses import run_active_arc_responses_loop
from framework.prompting.active_arc_tools import DEFAULT_OPENAI_MODEL


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="ActiveARC OpenAI agent (tool calling)")
    p.add_argument("--task-id", type=str, default=None, help="Task id (ARC: 8eb1be9a; ConceptARC: count/count11 or sample; P-ARC: test2_t1); omit for random eligible task.")
    p.add_argument(
        "--dataset",
        choices=["arc", "conceptarc", "parc"],
        default="arc",
        help="Task pool: arc (default), conceptarc, or parc (P-ARC).",
    )
    p.add_argument(
        "--sample-family",
        action="store_true",
        help="ConceptARC only: sample a new DSL task family online.",
    )
    p.add_argument(
        "--persist-sampled-family",
        action="store_true",
        help="ConceptARC only: persist a newly sampled family into the exported catalog.",
    )
    p.add_argument("--seed", type=int, default=0)
    p.add_argument(
        "--backend",
        choices=["responses", "chat"],
        default="responses",
        help="OpenAI API backend (default: responses — recommended for multi-turn tool loops).",
    )
    p.add_argument(
        "--model",
        type=str,
        default=None,
        help=f"OpenAI model name (default: env OPENAI_MODEL or {DEFAULT_OPENAI_MODEL}).",
    )
    p.add_argument("--max-turns", type=int, default=64)
    p.add_argument("--temperature", type=float, default=0.2, help="Chat backend only.")
    p.add_argument(
        "--reasoning-effort",
        type=str,
        default="low",
        help="Responses backend only: none|low|medium|high (default: low). Pass 'none' to omit.",
    )
    p.add_argument("--hot-start", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--noisy-science", action="store_true")
    p.add_argument("--re-trials", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument(
        "--fixed-test",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Keep one test sample for the whole trial (default: resample on each finish_exploration).",
    )
    p.add_argument("--noise-probability", type=float, default=0.12)
    p.add_argument(
        "--dump-transcript",
        type=str,
        default=None,
        help="Optional path to write full JSON result.",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    session = create_trial_session(
        seed=args.seed,
        task_id=args.task_id,
        hot_start=args.hot_start,
        noisy_science=args.noisy_science,
        re_trials=args.re_trials,
        noise_probability=args.noise_probability,
        dataset=args.dataset,
        sample_family=args.sample_family,
        persist_sampled_family=args.persist_sampled_family,
        fixed_test=args.fixed_test,
    )
    reasoning_effort = None if args.reasoning_effort.lower() == "none" else args.reasoning_effort
    if args.backend == "responses":
        result = run_active_arc_responses_loop(
            session,
            model=args.model,
            max_turns=args.max_turns,
            reasoning_effort=reasoning_effort,
        )
    else:
        result = run_openai_agent_loop(
            session,
            model=args.model,
            max_turns=args.max_turns,
            temperature=args.temperature,
        )
    out = build_trial_record(
        session,
        result,
        dataset=args.dataset,
        hot_start=args.hot_start,
        noisy_science=args.noisy_science,
        re_trials=args.re_trials,
        fixed_test=args.fixed_test,
    )
    text = json.dumps(out, indent=2)
    print(text)
    if args.dump_transcript:
        Path(args.dump_transcript).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
