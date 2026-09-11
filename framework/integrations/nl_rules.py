"""Verified natural-language rules for Inverse Query (ARC-AGI-1/2).

ARC-AGI-1 uses LARC descriptions that an independent human builder
reconstructed from language alone. ARC-AGI-2 uses MARC2 descriptions that
passed independent description-only solver validation.

Lookups are compact JSON under ``external/nl_rules/``. Rebuild with
``python -m pipelines.build_nl_rule_lookups``.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

_ACTIVEARC_ROOT = Path(__file__).resolve().parents[2]
NL_RULES_DIR = _ACTIVEARC_ROOT / "external" / "nl_rules"
LARC_PATH = NL_RULES_DIR / "larc_arc_agi_1.json"
MARC2_PATH = NL_RULES_DIR / "marc2_arc_agi_2.json"


def _normalize_task_id(task_id: str) -> str:
    tid = task_id.strip().lower()
    if tid.endswith(".json"):
        tid = tid[: -len(".json")]
    return tid


@lru_cache(maxsize=2)
def _load_rules(path: str) -> Dict[str, str]:
    p = Path(path)
    if not p.is_file():
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
