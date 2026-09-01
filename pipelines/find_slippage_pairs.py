#!/usr/bin/env python3
"""Find and save ARC-AGI-1 slippage pairs (narrow vs RE-ARC broad).

A pair qualifies when:

* **broad** (``re_arc``) is CSV-valid on the narrow distribution — original
  train + test, ARC-GEN stable, and ARC-GEN dynamic50;
* **narrow** (google / keymoon / neurips / custom) is also CSV-valid on that
  same distribution, but fails on ``>=`` majority of scored RE-ARC samples
  (default 50%).

Example::

    python -m pipelines.find_slippage_pairs \\
        --out experiments/slippage/slippage_pairs.json \\
        --max-re-arc-pairs 100

    # Quick smoke on a few tasks:
    python -m pipelines.find_slippage_pairs --num-tasks 20 --out /tmp/slippage_smoke.json
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from framework.slippage.pair_search import (
    candidate_task_ids,
    find_slippage_pairs,
    save_slippage_pairs,
)
from framework.verifier_selection import default_verifiers_csv_path


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Find ARC-AGI-1 slippage verifier pairs.")
    p.add_argument(
        "--out",
        type=Path,
        default=ROOT_DIR / "experiments" / "slippage" / "slippage_pairs.json",
        help="Output JSON path.",
    )
    p.add_argument(
        "--max-re-arc-pairs",
        type=int,
        default=200,
        help="Max RE-ARC stable pairs to score per task (from re_arc.zip).",
    )
    p.add_argument(
        "--max-re-arc-dynamic-pairs",
        type=int,
        default=0,
        help="Fresh RE-ARC generator pairs to append per task (0 = stable only).",
    )
    p.add_argument(
        "--majority-threshold",
        type=float,
        default=0.5,
        help="Narrow fail rate on RE-ARC samples must be >= this (default 0.5).",
    )
    p.add_argument(
        "--num-tasks",
        type=int,
        default=None,
        help="Optional cap on candidate tasks (after CSV prefilter).",
    )
    p.add_argument(
        "--task-id",
        action="append",
        default=None,
        help="Restrict to specific task id(s); may be repeated.",
    )
    p.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Override task_valid_verifiers.csv path.",
    )
    p.add_argument(
        "--pair-timeout",
        type=float,
        default=0.5,
        help="Per-example verifier timeout in seconds (timeouts count as fails).",
    )
    p.add_argument("--quiet", action="store_true", help="Less progress output.")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    csv_path = args.csv if args.csv is not None else default_verifiers_csv_path()

    if args.task_id:
        ids = list(dict.fromkeys(args.task_id))
    else:
        ids = candidate_task_ids(csv_path=csv_path)
        if args.num_tasks is not None:
            ids = ids[: max(0, args.num_tasks)]

    print(
        f"Scanning {len(ids)} candidate tasks "
        f"(max_re_arc_stable={args.max_re_arc_pairs}, "
        f"max_re_arc_dynamic={args.max_re_arc_dynamic_pairs}, "
        f"narrow_fail≥{args.majority_threshold}, "
        f"pair_timeout={args.pair_timeout}s)",
        flush=True,
    )

    pairs = find_slippage_pairs(
        ids,
        max_re_arc_pairs=args.max_re_arc_pairs,
        max_re_arc_dynamic_pairs=args.max_re_arc_dynamic_pairs,
        majority_threshold=args.majority_threshold,
        pair_timeout_s=args.pair_timeout,
        csv_path=csv_path,
        progress=not args.quiet,
    )

    meta = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "csv": str(csv_path),
        "n_candidates_scanned": len(ids),
        "max_re_arc_pairs": args.max_re_arc_pairs,
        "max_re_arc_dynamic_pairs": args.max_re_arc_dynamic_pairs,
        "majority_threshold": args.majority_threshold,
        "pair_timeout_s": args.pair_timeout,
        "broad_slot": "re_arc",
        "narrow_slots": ["google", "keymoon", "neurips", "custom"],
        "criterion": (
            "Broad (re_arc) and narrow slots are both CSV-valid on the narrow "
            "distribution (train + test + ARC-GEN stable + ARC-GEN dynamic50). "
            "Broad must pass 100% of scored RE-ARC stable + dynamic samples. "
            "Narrow fail_rate on those samples >= majority_threshold."
        ),
    }
    out = save_slippage_pairs(pairs, args.out, meta=meta)
    by_narrow: dict[str, int] = {}
    for p in pairs:
        by_narrow[p.narrow_slot] = by_narrow.get(p.narrow_slot, 0) + 1
    print(
        f"Wrote {len(pairs)} pairs across {len({p.task_id for p in pairs})} tasks → {out}",
        flush=True,
    )
    if by_narrow:
        print("By narrow slot:", by_narrow, flush=True)


if __name__ == "__main__":
    main()
