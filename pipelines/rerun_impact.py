#!/usr/bin/env python3
"""Which recorded trials were judged by a verifier the census rejects.

    python -m pipelines.rerun_impact

A trial pinned to a slot that turned out to be wrong was run against a bad
oracle and has to be re-run.  A trial pinned to a slot that is merely *not* the
canonical one is still sound evidence -- the oracle agreed with the generator
everywhere the census looked -- so it is reported separately rather than lumped
into the same bucket.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

SKIP = {"manifest.json", "summary.json", "summary.jsonl", "program_scores.json"}


def main() -> None:
    from pipelines.apply_canon_verifiers import choose

    tables = {}
    for ds in ("arc", "arc2"):
        try:
            tables[ds] = choose(ds)[0]
        except Exception as exc:
            print("no census for %s (%s)" % (ds, exc))
            tables[ds] = {}

    runs = sorted(p for p in (ROOT_DIR / "experiments" / "runs").iterdir() if p.is_dir())
    print("%-46s %5s %7s %7s %7s" % ("run", "n", "canon", "other-ok", "REJECTED"))
    grand: Dict[str, List[str]] = {}
    for run in runs:
        n = canon_ok = other_ok = bad = 0
        bad_ids: List[str] = []
        for f in sorted(run.glob("*.json")):
            if f.name in SKIP:
                continue
            try:
                rec = json.loads(f.read_text())
            except Exception:
                continue
            tid = rec.get("task_id")
            slot = (rec.get("trial") or {}).get("verifier_slot") or rec.get("verifier_slot")
            if not tid or not slot:
                continue
            entry = tables.get("arc", {}).get(tid) or tables.get("arc2", {}).get(tid)
            if entry is None:
                continue
            n += 1
            rejected_slots = {k.split(":", 1)[1] for k in entry["rejected"]}
            canon = (entry.get("canon") or {}).get("slot")
            if slot in rejected_slots and slot != canon:
                bad += 1
                bad_ids.append(tid)
            elif slot == canon:
                canon_ok += 1
            else:
                other_ok += 1
        if n:
            print("%-46s %5d %7d %7d %7d" % (run.name, n, canon_ok, other_ok, bad))
            if bad_ids:
                grand[run.name] = bad_ids
    print()
    if grand:
        print("trials to re-run, by run:")
        for k, v in grand.items():
            print("   %-44s %3d  %s" % (k, len(v), " ".join(sorted(set(v)))[:160]))
    else:
        print("no recorded trial was judged by a rejected verifier.")


if __name__ == "__main__":
    main()
