#!/usr/bin/env python3
"""Mark runs whose test items were answered in one shared context.

Before the branched test phase landed, a trial with several held-out items was
shown all of them together and answered them in a single call. The per-item
results from those runs are therefore not independent measurements: each answer
was given having seen the other items' input grids, so they cannot be compared
against the static arm or against single-item runs, both of which see one grid
at a time.

The finding is recorded in three places so it cannot be missed later: an
``INVALID_shared_test_context.json`` marker beside the run, a ``README`` note in
plain sight, and a ``shared_test_context`` block written into each affected
trial record and the run summary.

Detection is from the data, not a hardcoded list: a trial is affected if it
carries two or more ``test_item_kinds`` and its transcript has no per-item
branch markers (``test_item`` on a test-phase turn), which only the branched
implementation writes.

    python -m pipelines.flag_shared_test_context experiments/runs
    python -m pipelines.flag_shared_test_context experiments/runs --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

NON_TRIAL = {"manifest.json", "summary.json", "summary.jsonl",
             "program_scores.json", "oracle_recheck.json",
             "oracle_recheck_canon.json", "INVALID.json",
             "INVALID_shared_test_context.json"}

MARKER = "INVALID_shared_test_context.json"
README = "README_INVALID.txt"

NOTE = """\
DO NOT USE THE PER-ITEM RESULTS IN THIS RUN.

Every trial here with more than one held-out test item was shown all of them in
one message and answered them in a single call. Each answer was therefore given
having seen the other items' input grids, so `test_item_correct` entries are not
independent measurements.

What that rules out:
  - comparing per-item accuracy against the static arm, which answers one test
    item at a time in a fresh context;
  - comparing against single-item runs (anything without --test-source both);
  - reading the official-vs-sampled difference as a property of the items.

What still holds:
  - the all-items-correct `correct` field remains a valid joint measure;
  - trials with only one test item are unaffected.

Re-run with the branched test phase (each item answered on its own fork of the
exploration conversation) to obtain independent per-item results.

Affected trials: {n_affected} of {n_trials}
Flagged at: {when}
"""


def trial_files(run: Path):
    for f in sorted(run.glob("*.json")):
        if f.name not in NON_TRIAL:
            yield f


def is_shared(rec: dict) -> bool:
    """Several items, and no per-item branch markers in the transcript."""
    if len(rec.get("test_item_kinds") or []) < 2:
        return False
    for turn in rec.get("transcript") or []:
        if turn.get("phase") == "test" and turn.get("test_item") is not None:
            return False   # branched: each item has its own marked turns
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default="experiments/runs")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        raise SystemExit(f"No such directory: {root}")

    when = datetime.now(timezone.utc).isoformat()
    total_runs = total_trials = 0

    for run in sorted(p for p in root.iterdir() if p.is_dir()):
        files = list(trial_files(run))
        if not files:
            continue
        affected = []
        for f in files:
            try:
                rec = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            if is_shared(rec):
                affected.append((f, rec))
        if not affected:
            continue

        total_runs += 1
        total_trials += len(affected)
        print(f"{run.name:34} {len(affected):>5} of {len(files):>5} trials affected")
        if args.dry_run:
            continue

        stamp = {
            "shared_test_context": True,
            "reason": "test items shown together and answered in one call; "
                      "per-item results are not independent",
            "flagged_at": when,
        }
        for f, rec in affected:
            rec["shared_test_context"] = stamp
            f.write_text(json.dumps(rec, indent=2), encoding="utf-8")

        (run / MARKER).write_text(json.dumps({
            **stamp,
            "run": run.name,
            "n_affected": len(affected),
            "n_trials": len(files),
        }, indent=2), encoding="utf-8")
        (run / README).write_text(
            NOTE.format(n_affected=len(affected), n_trials=len(files), when=when),
            encoding="utf-8")

        summary = run / "summary.json"
        if summary.is_file():
            try:
                s = json.loads(summary.read_text(encoding="utf-8"))
                s["shared_test_context"] = {**stamp, "n_affected": len(affected)}
                summary.write_text(json.dumps(s, indent=2), encoding="utf-8")
            except Exception:
                pass

    verb = "would flag" if args.dry_run else "flagged"
    print(f"\n{verb} {total_trials} trials across {total_runs} runs")
    if not args.dry_run and total_runs:
        print(f"each run carries {MARKER} and {README}")


if __name__ == "__main__":
    sys.exit(main())
