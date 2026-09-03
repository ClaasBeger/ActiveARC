#!/usr/bin/env python3
"""Retry pending_timeout AGI-2 verifier candidates with a large timeout budget."""

from __future__ import annotations

import json
import logging
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.import_agi2_verifiers.collect import v2_task_ids
from scripts.import_agi2_verifiers.paths import CANDIDATES, LOGS, OUT
from scripts.import_agi2_verifiers.validate import (
    coverage_report,
    promote_valid,
    run_validation,
)


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOGS / "pending_timeout_retry.log"),
        ],
    )
    log = logging.getLogger("pending_retry")

    final_path = LOGS / "final_results.json"
    prev = {r["candidate_id"]: r for r in json.loads(final_path.read_text())}
    pending_ids = {cid for cid, r in prev.items() if r.get("status") == "pending_timeout"}
    metas = []
    for meta_path in sorted(CANDIDATES.glob("*/*.py.meta.json")):
        meta = json.loads(meta_path.read_text())
        if meta["candidate_id"] in pending_ids:
            metas.append(meta_path)

    case_timeout = 60.0
    overall_timeout = 300.0  # allow real dynamic work after common.py fix
    workers = 8
    pass_number = 5
    log.info(
        "Retrying %d pending_timeout candidates (pass=%d case_timeout=%ss overall=%ss workers=%d)",
        len(metas),
        pass_number,
        case_timeout,
        overall_timeout,
        workers,
    )
    if not metas:
        log.info("Nothing to retry")
        return 0

    results = run_validation(
        metas,
        workers=workers,
        pass_number=pass_number,
        timeout_s=case_timeout,
        overall_timeout_s=overall_timeout,
        resume=False,
    )

    for r in results:
        prev[r["candidate_id"]] = r
    final = list(prev.values())
    promote_valid(final)
    report = coverage_report(final, v2_task_ids())
    summary = {
        "n_candidates": len(final),
        "n_promoted_valid": report["n_valid_candidates"],
        "coverage": report,
        f"pass{pass_number}_pending_retry": {
            "n": len(results),
            "status": dict(Counter(r["status"] for r in results)),
        },
    }
    (OUT / "import_summary.json").write_text(json.dumps(summary, indent=2))
    final_path.write_text(json.dumps(final, indent=2))
    key = f"pass{pass_number}_pending_retry"
    log.info(
        "DONE pass%d status=%s | valid_candidates=%d tasks_covered=%d/%d pending_left=%d",
        pass_number,
        summary[key]["status"],
        report["n_valid_candidates"],
        report["tasks_with_ge1_valid"],
        report["n_v2_tasks"],
        report["n_pending_timeout"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
