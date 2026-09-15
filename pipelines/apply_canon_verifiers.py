#!/usr/bin/env python3
"""Record the canonical verifier per task, from the slot census.

    python -m pipelines.apply_canon_verifiers            # dry run
    python -m pipelines.apply_canon_verifiers --write

ARC-AGI-1 canon goes in ``task_valid_verifiers.csv``'s ``selected_verifier_slot``
column (the file keeps its CRLF line endings); ARC-AGI-2 canon goes in
``external/agi2_verifiers/canon.json``.  ``pick_verifier`` consults both before
falling back to slot preference, so a task is judged by one verifier and the
same one on every seed.

A slot is canon-eligible only if, over the census draw, it reproduces the task's
own official examples, never raises or times out, and never contradicts the
generator -- except on a task in ``KNOWN_AMBIGUOUS``, where the generator's own
choice is unrecoverable and a mismatch says nothing about the verifier.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

PRIORITY = ("custom", "re_arc", "google", "keymoon", "neurips")
CSV_PATH = ROOT_DIR / "task_valid_verifiers.csv"
AGI2_CANON = ROOT_DIR / "external" / "agi2_verifiers" / "canon.json"


def _rows(dataset: str) -> List[dict]:
    stream = ROOT_DIR / "experiments" / ("verifier_slot_audit_%s.jsonl" % dataset)
    if stream.is_file():
        return [json.loads(l) for l in stream.read_text().splitlines() if l.strip()]
    whole = ROOT_DIR / "experiments" / ("verifier_slot_audit_%s.json" % dataset)
    return json.loads(whole.read_text())["rows"]


def _excepted(task_id: str) -> int:
    """Official pairs that contradict their own task's rule.

    A verifier that follows the rule cannot reproduce these, and the vendored
    ones that do only manage it with a hash()-keyed special case. Holding them
    against a verifier would canonise the cheat over the honest implementation.
    """
    from framework.active_arc.program_eval import OFFICIAL_PAIR_EXCEPTIONS

    return sum(len(v) for v in (OFFICIAL_PAIR_EXCEPTIONS.get(task_id) or {}).values())


def _eligible(row: dict, stats: dict, ambiguous: bool) -> Optional[str]:
    """``None`` if the slot may be canon, else why not."""
    need = row.get("n_official", 0) - _excepted(row["task_id"])
    if stats["official_ok"] < need:
        return "fails its own examples (%d/%d)" % (stats["official_ok"], need)
    if stats.get("errored"):
        return "%d/%d generated inputs raise%s" % (
            stats["errored"], row.get("n_pairs", 0),
            " or time out" if stats.get("timeouts") else "")
    if stats.get("mismatched") and not ambiguous:
        return "disagrees on %d/%d generated pairs" % (stats["mismatched"], row.get("n_pairs", 0))
    return None


def choose(dataset: str) -> Tuple[Dict[str, dict], List[str]]:
    from framework.tasks.pair_guard import KNOWN_AMBIGUOUS

    out: Dict[str, dict] = {}
    homeless: List[str] = []
    for row in _rows(dataset):
        tid = row["task_id"]
        if row.get("error"):
            out[tid] = {"canon": None, "why": row["error"], "rejected": {}}
            homeless.append(tid)
            continue
        ok: List[Tuple[str, int, str]] = []
        rejected: Dict[str, str] = {}
        for key, stats in (row.get("slots") or {}).items():
            why = _eligible(row, stats, tid in KNOWN_AMBIGUOUS)
            if why:
                rejected[key] = why
            else:
                ok.append((stats["slot"], stats["index"], key))
        pick = None
        for slot in PRIORITY:
            hit = [o for o in ok if o[0] == slot]
            if hit:
                pick = hit[0]
                break
        if pick is None and ok:
            pick = ok[0]
        if pick is None:
            homeless.append(tid)
        out[tid] = {
            "canon": None if pick is None else {"slot": pick[0], "index": pick[1], "key": pick[2]},
            "rejected": rejected,
            "n_pairs": row.get("n_pairs"),
            "n_official": row.get("n_official"),
        }
    return out, homeless


def write_csv(canon: Dict[str, dict]) -> Tuple[int, int]:
    """Set ``selected_verifier_slot`` from *canon*. Byte-level, so CRLF survives."""
    raw = CSV_PATH.read_bytes().decode("utf-8")
    lines = raw.split("\r\n")
    header = lines[0].split(",")
    i_tid = header.index("task_id")
    i_sel = header.index("selected_verifier_slot")
    changed = kept = 0
    for n, line in enumerate(lines[1:], start=1):
        if not line.strip():
            continue
        cells = line.split(",")
        entry = canon.get(cells[i_tid])
        if not entry or not entry.get("canon"):
            continue
        want = entry["canon"]["slot"]
        if cells[i_sel] == want:
            kept += 1
            continue
        cells[i_sel] = want
        lines[n] = ",".join(cells)
        changed += 1
    CSV_PATH.write_bytes("\r\n".join(lines).encode("utf-8"))
    return changed, kept


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    arc, arc_homeless = choose("arc")
    arc2, arc2_homeless = choose("arc2")

    for label, table, homeless in (("ARC-AGI-1", arc, arc_homeless),
                                   ("ARC-AGI-2", arc2, arc2_homeless)):
        n_rej = sum(len(v["rejected"]) for v in table.values())
        byslot: Dict[str, int] = {}
        for v in table.values():
            if v["canon"]:
                byslot[v["canon"]["slot"]] = byslot.get(v["canon"]["slot"], 0) + 1
        print("%s: %d tasks | canon %s | slots rejected %d | no clean verifier %d %s" % (
            label, len(table), byslot, n_rej, len(homeless), homeless or ""))

    if not args.write:
        print("\n(dry run; pass --write to record)")
        return

    changed, kept = write_csv(arc)
    print("csv: %d selected_verifier_slot changed, %d already canonical" % (changed, kept))

    AGI2_CANON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_meta": {
            "why": "One promoted candidate per task is the one to judge by; several "
                   "can be valid and still differ off the audited distribution.",
            "built_by": "python -m pipelines.apply_canon_verifiers --write",
        },
        "canon": {t: v["canon"]["key"].split(":", 1)[1] if False else v["canon"]["slot"]
                  for t, v in arc2.items() if v["canon"]},
    }
    # For ARC-AGI-2 every slot is named "custom"; the candidate id is what
    # distinguishes them, so record that instead of the slot name.
    from framework.integrations.agi2_verifiers import list_agi2_valid_candidate_ids
    payload["canon"] = {}
    for t, v in arc2.items():
        if not v["canon"]:
            continue
        cids = list_agi2_valid_candidate_ids(t)
        idx = v["canon"]["index"]
        # index 0 may be the local fixes/ verifier, which has no candidate id;
        # in that case there is nothing to pin here and slot order already wins.
        offset = len(_local_offset(t))
        j = idx - offset
        if 0 <= j < len(cids):
            payload["canon"][t] = cids[j]
    AGI2_CANON.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print("wrote %s (%d tasks)" % (AGI2_CANON, len(payload["canon"])))


def _local_offset(task_id: str) -> List[str]:
    """The locally written verifiers that sit ahead of the vendored candidates."""
    try:
        from framework.custom_verifiers.registry import has_local_verifier
        return ["local"] if has_local_verifier(task_id) else []
    except Exception:
        return []


if __name__ == "__main__":
    main()
