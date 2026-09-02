"""Import + validate standalone verifiers for ARC-GEN ARC-AGI-2 (V2) tasks.

Usage:
  python -m scripts.import_agi2_verifiers --workers 6
  python -m scripts.import_agi2_verifiers --collect-only
  python -m scripts.import_agi2_verifiers --validate-only
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from .collect import collect_all, v2_task_ids
from .paths import CANDIDATES, LOGS, OUT, ROOT
from .validate import (
    TIMEOUT_PASS1,
    TIMEOUT_PASS2,
    coverage_report,
    promote_valid,
    run_validation,
)


def _setup_logging() -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOGS / "import_agi2_verifiers.log"),
        ],
    )


def _all_meta_paths():
    return sorted(CANDIDATES.glob("*/*.py.meta.json"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collect-only", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--limit", type=int, default=0, help="Validate at most N candidates (debug)")
    parser.add_argument("--pass1-timeout", type=float, default=TIMEOUT_PASS1)
    parser.add_argument("--pass2-timeout", type=float, default=TIMEOUT_PASS2)
    args = parser.parse_args(argv)

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    _setup_logging()
    log = logging.getLogger("main")

    if not args.validate_only:
        metas = collect_all()
        log.info("Collected %d candidates", len(metas))
        if args.collect_only:
            return 0

    meta_paths = _all_meta_paths()
    if args.limit:
        meta_paths = meta_paths[: args.limit]
    log.info("Validating %d candidates (workers=%d)", len(meta_paths), args.workers)

    pass1 = run_validation(
        meta_paths,
        workers=args.workers,
        pass_number=1,
        timeout_s=args.pass1_timeout,
    )
    pending_metas = []
    for r in pass1:
        if r["status"] == "pending_timeout":
            cand = CANDIDATES / r["relative_path"]
            meta = cand.with_suffix(cand.suffix + ".meta.json")
            if meta.is_file():
                pending_metas.append(meta)

    pass2: list = []
    if pending_metas:
        log.info(
            "Second pass for %d pending_timeout candidates (timeout=%ss)",
            len(pending_metas),
            args.pass2_timeout,
        )
        pass2 = run_validation(
            pending_metas,
            workers=max(1, min(args.workers, len(pending_metas))),
            pass_number=2,
            timeout_s=args.pass2_timeout,
            overall_timeout_s=max(900.0, args.pass2_timeout * 40),
            resume=False,
        )

    # Merge: start from pass1, replace pending with pass2 outcomes
    by_id = {r["candidate_id"]: r for r in pass1}
    for r in pass2:
        by_id[r["candidate_id"]] = r
    final = list(by_id.values())

    n_promoted = promote_valid(final)
    v2 = v2_task_ids()
    report = coverage_report(final, v2)
    summary = {
        "n_candidates": len(final),
        "n_promoted_valid": n_promoted,
        "coverage": report,
        "pass2_n": len(pass2),
    }
    (OUT / "import_summary.json").write_text(json.dumps(summary, indent=2))
    (LOGS / "final_results.json").write_text(json.dumps(final, indent=2))
    log.info(
        "DONE valid_candidates=%d tasks_covered=%d/%d pending_left=%d",
        report["n_valid_candidates"],
        report["tasks_with_ge1_valid"],
        report["n_v2_tasks"],
        report["n_pending_timeout"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
