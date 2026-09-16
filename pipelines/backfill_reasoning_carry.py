#!/usr/bin/env python3
"""Stamp how each recorded trial carried the model's reasoning across turns.

``n_reasoning_details`` counts reasoning blocks replayed in a request. That only
means anything where the conversation is resent: on OpenAI the chain holds the
reasoning server-side, nothing about it appears in the request, and the count is
absent because it does not apply -- not because thinking was dropped. Reading
those runs without knowing that makes them look broken when they are fine.

Runs recorded before ``reasoning_carry`` existed get it added here, derived from
the provider already in the record, so the distinction survives without anyone
having to remember it. ``usage.reasoning_tokens`` is reported alongside as the
positive evidence that thinking happened either way.

    python -m pipelines.backfill_reasoning_carry experiments/runs
    python -m pipelines.backfill_reasoning_carry experiments/runs --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from framework.prompting.clients import reasoning_carry  # noqa: E402

NON_TRIAL = {"manifest.json", "summary.json", "summary.jsonl",
             "program_scores.json", "oracle_recheck.json",
             "oracle_recheck_canon.json", "INVALID.json",
             "INVALID_shared_test_context.json"}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default="experiments/runs")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        raise SystemExit(f"No such directory: {root}")

    totals: dict[str, int] = {}
    for run in sorted(p for p in root.iterdir() if p.is_dir()):
        stamped = 0
        kinds: dict[str, int] = {}
        thinking = 0
        for f in sorted(run.glob("*.json")):
            if f.name in NON_TRIAL:
                continue
            try:
                rec = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            provider = rec.get("provider")
            if not provider or rec.get("error"):
                continue
            how = reasoning_carry(provider)
            kinds[how] = kinds.get(how, 0) + 1
            if (rec.get("usage") or {}).get("reasoning_tokens"):
                thinking += 1
            if rec.get("reasoning_carry") == how:
                continue
            rec["reasoning_carry"] = how
            stamped += 1
            if not args.dry_run:
                f.write_text(json.dumps(rec, indent=2), encoding="utf-8")
        if not kinds:
            continue
        for k, v in kinds.items():
            totals[k] = totals.get(k, 0) + v
        detail = ", ".join(f"{k}={v}" for k, v in sorted(kinds.items()))
        print(f"{run.name:34} {detail:34} with_thinking={thinking:>4} stamped={stamped}")

    verb = "would stamp" if args.dry_run else "stamped"
    print(f"\n{verb}; trials by mechanism: {totals}")
    print("server_side = reasoning held by the provider's chain; a missing "
          "n_reasoning_details there is expected, not a fault.")


if __name__ == "__main__":
    sys.exit(main())
