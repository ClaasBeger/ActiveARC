#!/usr/bin/env python3
"""Sum the estimated USD of one or more run directories (per-record usage).

    python -m pipelines.spend experiments/runs/foiltest_arc25_luna_*
"""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from framework.prompting.pricing import estimate_usd  # noqa: E402


def dir_cost(d: str):
    total = 0.0
    n = 0
    toks = 0
    for f in glob.glob(f"{d}/*.json"):
        if f.endswith(("manifest.json", "summary.json")):
            continue
        r = json.loads(Path(f).read_text())
        if "error" in r:
            continue
        usage = r.get("usage") or {}
        # teacher records keep the exam separately
        exam = r.get("teacher_exam") or {}
        for tr in exam.get("transcript", []):
            u = (tr.get("response") or {}).get("usage") or {}
            for k in ("input_tokens", "cached_input_tokens", "output_tokens"):
                usage[k] = (usage.get(k) or 0) + (u.get(k) or 0)
        c = estimate_usd(r.get("model") or "gpt-5.6-luna", usage)
        if c is not None:
            total += c
            n += 1
            toks += usage.get("total_tokens") or (usage.get("input_tokens", 0) + usage.get("output_tokens", 0))
    return total, n, toks


def main() -> None:
    grand = 0.0
    for pattern in sys.argv[1:]:
        for d in sorted(glob.glob(pattern)):
            c, n, toks = dir_cost(d)
            grand += c
            print(f"{Path(d).name:<45} tasks={n:<3} tokens={toks:>10,}  ${c:.3f}")
    print(f"{'TOTAL':<45} {'':<9} {'':>17}  ${grand:.3f}")


if __name__ == "__main__":
    main()
