"""Verified natural-language rules for Inverse Query (ARC-AGI-1/2).

ARC-AGI-1 uses LARC descriptions that an independent human builder
reconstructed from language alone. ARC-AGI-2 uses MARC2 descriptions that
passed independent description-only solver validation.

Lookups are compact JSON under ``external/nl_rules/``. Rebuild with
``python -m pipelines.build_nl_rule_lookups``.
"""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, Tuple

from framework.repo_paths import ACTIVEARC_ROOT as _REPO_ROOT

# Via repo_paths, not this file's parents: the lookups are untracked, so they
# exist only in the main checkout. Resolved relative to __file__, a run from a
# git worktree looks inside the worktree, finds nothing, and hands the teacher
# no rule at all -- for every ARC-AGI-1, ARC-AGI-2 and P-ARC task, silently,
# because a missing file and a task with no rule are the same empty dict.
_ACTIVEARC_ROOT = _REPO_ROOT
NL_RULES_DIR = _ACTIVEARC_ROOT / "external" / "nl_rules"
LARC_PATH = NL_RULES_DIR / "larc_arc_agi_1.json"
MARC2_PATH = NL_RULES_DIR / "marc2_arc_agi_2.json"


def _normalize_task_id(task_id: str) -> str:
    tid = task_id.strip().lower()
    if tid.endswith(".json"):
        tid = tid[: -len(".json")]
    return tid


_warned: set = set()


def _warn_missing(p: Path) -> None:
    """Say once that a lookup is absent, rather than degrade quietly.

    Every caller treats "no rules" as "this task has no rule", which is a
    legitimate state, so an absent file otherwise costs a whole dataset's rules
    without a word.
    """
    key = str(p)
    if key not in _warned:
        _warned.add(key)
        print(f"[nl_rules] lookup not found: {p} -- rules from it will be "
              f"reported as unavailable", file=sys.stderr)


@lru_cache(maxsize=2)
def _load_rules(path: str) -> Dict[str, str]:
    p = Path(path)
    if not p.is_file():
        _warn_missing(p)
        return {}
    payload = json.loads(p.read_text(encoding="utf-8"))
    rules = payload.get("rules") if isinstance(payload, dict) else None
    if not isinstance(rules, dict):
        return {}
    return {str(k).strip().lower(): str(v).strip() for k, v in rules.items() if v}


def larc_rule(task_id: str) -> Optional[str]:
    """LARC builder-validated NL rule for an ARC-AGI-1 training task, if any."""
    text = _load_rules(str(LARC_PATH)).get(_normalize_task_id(task_id))
    return text or None


def marc2_rule(task_id: str) -> Optional[str]:
    """MARC2 language-complete NL rule for an ARC-AGI-2 training task, if any."""
    text = _load_rules(str(MARC2_PATH)).get(_normalize_task_id(task_id))
    return text or None


COLLECTED_PATH = NL_RULES_DIR / "collected_rules.json"
_COLLECTED_KEY = {"arc": "arc_agi_1", "arc2": "arc_agi_2", "parc": "parc", "conceptarc": "conceptarc"}


def collected_rule(task_id: str, dataset: str) -> Optional[Tuple[str, str]]:
    """``(rule, source)`` from the aggregate the annotation pipeline writes.

    The aggregate holds the published lookups *and* the hand-written drafts that
    close their gaps, each tagged with where it came from ("larc", "marc2",
    "draft", ...). Falls back to the published lookup alone when the aggregate is
    absent, so a checkout without it still gets what it had before.
    """
    tid = _normalize_task_id(task_id)
    key = _COLLECTED_KEY.get(dataset)
    if key and COLLECTED_PATH.is_file():
        try:
            block = json.loads(COLLECTED_PATH.read_text(encoding="utf-8")).get(key) or {}
        except Exception:
            block = {}
        entry = block.get(tid)
        if isinstance(entry, dict) and str(entry.get("rule") or "").strip():
            return str(entry["rule"]).strip(), str(entry.get("source") or "collected")
    if dataset == "arc":
        rule = larc_rule(tid)
        return (rule, "larc") if rule else None
    if dataset == "arc2":
        rule = marc2_rule(tid)
        return (rule, "marc2") if rule else None
    return None
