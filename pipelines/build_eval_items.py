#!/usr/bin/env python3
"""Freeze the sampled held-out item each task is scored on.

Draws each task's item once, before anything else touches the session RNG, and
writes them to ``experiments/eval_items/<dataset>_seed<seed>.json``. Every arm
then reads the same item instead of deriving its own, which a live draw cannot
guarantee: the random-K arm consumes the RNG drawing its demonstration pairs and
would otherwise land on a different item than the active arm did.

With ``--verify-against`` the drawn values are checked against a recorded run
before anything is written, so freezing can be shown not to move the item that
existing trials were scored on.

    python -m pipelines.build_eval_items --dataset arc --limit 400
    python -m pipelines.build_eval_items --dataset arc --limit 400 \\
        --verify-against experiments/runs/sciK_arc400_astra_s0_b
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from framework.tasks.eval_items import EVAL_ITEMS_DIR, draw_sampled_item, manifest_path
from pipelines.run_active_arc_batch import _output_basename, _task_ids


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Freeze sampled held-out items")
    p.add_argument("--dataset", choices=["arc", "arc2", "conceptarc", "parc"], default="arc")
    p.add_argument("--limit", type=int, default=400)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--per-concept-limit", type=int, default=None)
    p.add_argument("--task-id", action="append", dest="task_ids", default=None)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--from-run", type=str, default=None,
                   help="Take each item from this recorded run's trial.test_input "
                        "instead of redrawing. The canonical item is the one the "
                        "trials were actually scored on, and for P-ARC and ConceptARC "
                        "a fresh draw does not reproduce it: those sessions resolve "
                        "the hot-start pair against a pre-sampled test pair, so the "
                        "RNG has moved by the time the item would be drawn.")
    p.add_argument("--verify-against", type=str, default=None,
                   help="A recorded run directory; the drawn items must match the "
                        "trial.test_input it already used, or nothing is written.")
    p.add_argument("--force", action="store_true",
                   help="Write even where verification disagrees.")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    task_ids = _task_ids(args)
    if not task_ids:
        raise SystemExit("No task ids selected.")

    items = {}
    missing = []
    source = "run" if args.from_run else "draw"
    run_dir = Path(args.from_run) if args.from_run else None
    for i, task_id in enumerate(task_ids, start=1):
        got = None
        if run_dir is not None:
            f = run_dir / f"{_output_basename(task_id)}.json"
            if f.is_file():
                rec = json.loads(f.read_text(encoding="utf-8"))
                trial = rec.get("trial") or {}
                ti = trial.get("test_input")
                if ti is not None and "error" not in rec:
                    # the gold output is whatever the trial was scored against
                    kinds = rec.get("test_item_kinds") or []
                    got = (ti, trial.get("test_output"))
        if got is None or got[1] is None:
            drawn = draw_sampled_item(args.dataset, args.seed, task_id)
            if drawn is None:
                missing.append(task_id)
                continue
            if got is not None and got[0] is not None and drawn[0] != got[0]:
                # recorded input wins; recompute its output from the verifier
                from framework.active_arc.headless_trial import create_trial_session
                sess = create_trial_session(seed=args.seed, task_id=task_id, dataset=args.dataset)
                got = (got[0], sess._verifier_fn()(got[0]))
            else:
                got = drawn
        items[task_id] = {"input": got[0], "output": got[1]}
        if i % 50 == 0:
            print(f"  {source} {i}/{len(task_ids)}", flush=True)

    mismatches = []
    if args.verify_against:
        run = Path(args.verify_against)
        checked = 0
        for task_id, entry in items.items():
            f = run / f"{_output_basename(task_id)}.json"
            if not f.is_file():
                continue
            rec = json.loads(f.read_text(encoding="utf-8"))
            if "error" in rec:
                continue
            recorded = (rec.get("trial") or {}).get("test_input")
            if recorded is None:
                continue
            checked += 1
            if recorded != entry["input"]:
                mismatches.append(task_id)
        print(f"verified against {run.name}: {checked} checked, {len(mismatches)} mismatched")
        if mismatches and not args.force:
            print("  first few:", mismatches[:8])
            raise SystemExit("Refusing to write: freezing would move items that "
                             "recorded trials were scored on. Re-run with --force "
                             "only if that is intended.")

    EVAL_ITEMS_DIR.mkdir(parents=True, exist_ok=True)
    out = manifest_path(args.dataset, args.seed)
    out.write_text(json.dumps({
        "dataset": args.dataset,
        "seed": args.seed,
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "n_items": len(items),
        "n_unavailable": len(missing),
        "unavailable": missing,
        "verified_against": args.verify_against,
        "n_mismatched": len(mismatches),
        "items": items,
    }, indent=1), encoding="utf-8")
    print(f"wrote {out} — {len(items)} items, {len(missing)} unavailable")


if __name__ == "__main__":
    sys.exit(main())
