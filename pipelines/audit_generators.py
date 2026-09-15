#!/usr/bin/env python3
"""Check that every ARC-GEN generator still reproduces the task it stands for.

    python -m pipelines.audit_generators --dataset arc --jobs 8

``validate()`` calls ``generate()`` with the official parameters, so a generator
that cannot reproduce its own train/test examples is broken regardless of what
its sampling branch does.  Also drawn once unparameterised, to catch a sampler
that raises or hangs.

Writes ``experiments/generator_audit_<dataset>.json``.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def _check(payload) -> Dict[str, Any]:
    task_id, dataset = payload
    from framework.tasks.arc_dataset import load_task

    out: Dict[str, Any] = {"task_id": task_id}
    try:
        task = load_task(task_id, load_alternative_verifiers=False)
    except Exception as exc:
        return dict(out, error="load: %s" % exc)

    official = [(p.input, p.output) for p in task.train_pairs] + \
               list(zip(task.test_inputs, task.test_outputs))
    out["n_official"] = len(official)

    # 1. the authored examples, through the generator's own validate()
    try:
        from framework.tasks.arc_dataset import _arc_gen_id_to_task_num_and_generator
        mod = _arc_gen_id_to_task_num_and_generator(task_id)
    except Exception:
        mod = None
    produced: List[Any] = []
    if mod:
        try:
            _num, gen_fn = mod
            # the helper hands back generate(); validate() lives beside it
            import sys as _sys
            gen_mod = _sys.modules[gen_fn.__module__]
            v = gen_mod.validate()
            produced = [(e["input"], e["output"]) for e in v.get("train", [])] + \
                       [(e["input"], e["output"]) for e in v.get("test", [])]
        except Exception as exc:
            out["validate_error"] = "%s: %s" % (type(exc).__name__, exc)
    out["n_validate"] = len(produced)
    if produced:
        prod = {(json.dumps(i), json.dumps(o)) for i, o in produced}
        missing = [k for k, (i, o) in enumerate(official)
                   if (json.dumps(i), json.dumps(o)) not in prod]
        out["official_missing"] = missing
        out["official_ok"] = len(official) - len(missing)

    # 2. the sampling branch
    gen = task.arc_gen_generator
    if gen is None:
        out["sampler"] = "absent"
        return out
    drawn = 0
    try:
        for s in range(3):
            drawn += len(gen(s))
        out["sampler"] = "ok"
        out["drawn"] = drawn
    except Exception as exc:
        out["sampler"] = "%s: %s" % (type(exc).__name__, exc)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", choices=("arc", "arc2"), default="arc")
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()

    if args.dataset == "arc":
        from framework.tasks.arc_dataset import list_arc_agi_1_task_ids
        ids = list(list_arc_agi_1_task_ids())
    else:
        from framework.integrations.agi2_verifiers import _index
        ids = sorted(_index().keys())

    rows: List[Dict[str, Any]] = []
    ctx = mp.get_context("spawn")
    with ctx.Pool(processes=args.jobs) as pool:
        for i, row in enumerate(pool.imap_unordered(_check, [(t, args.dataset) for t in ids]), 1):
            rows.append(row)
            bad = row.get("error") or row.get("validate_error") or \
                (row.get("sampler") not in ("ok", "absent")) or row.get("official_missing")
            if bad:
                print("[%d/%d] %s  %s" % (i, len(ids), row["task_id"], json.dumps(
                    {k: v for k, v in row.items() if k != "task_id"})[:160]), flush=True)
    out = ROOT_DIR / "experiments" / ("generator_audit_%s.json" % args.dataset)
    out.write_text(json.dumps({"dataset": args.dataset, "rows": rows}, indent=1), encoding="utf-8")
    n_bad = sum(1 for r in rows if r.get("error") or r.get("validate_error")
                or (r.get("sampler") not in ("ok", "absent")) or r.get("official_missing"))
    print("wrote %s | %d of %d generators with a problem" % (out, n_bad, len(rows)))


if __name__ == "__main__":
    main()
