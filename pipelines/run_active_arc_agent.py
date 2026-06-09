#!/usr/bin/env python3
"""Run an OpenAI tool-calling agent on one ActiveARC trial (same rules as the Streamlit UI).

Requires ``OPENAI_API_KEY``. Set ``OPENAI_MODEL`` to your chat model (e.g. ``gpt-4o`` or newer).

Example::

    python -m pipelines.run_active_arc_agent --task-id 8eb1be9a --seed 42

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
from framework.prompting.active_arc_openai import run_openai_agent_loop


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="ActiveARC OpenAI agent (tool calling)")
    p.add_argument("--task-id", type=str, default=None, help="ARC task id; omit for random eligible task.")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument(
        "--model",
        type=str,
        default=None,
        help="OpenAI model name (default: env OPENAI_MODEL or gpt-4o).",
    )
    p.add_argument("--max-turns", type=int, default=64)
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--hot-start", action="store_true")
    p.add_argument("--noisy-science", action="store_true")
    p.add_argument("--re-trials", action="store_true")
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
    )
    result = run_openai_agent_loop(
        session,
        model=args.model,
        max_turns=args.max_turns,
        temperature=args.temperature,
    )
    out = {
        "task_id": session.task_id,
        "seed": session.seed,
        "final": result.get("final"),
        "query_count": session.query_count,
        "phase": session.phase,
        "transcript": result.get("transcript"),
    }
    text = json.dumps(out, indent=2)
    print(text)
    if args.dump_transcript:
        Path(args.dump_transcript).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
