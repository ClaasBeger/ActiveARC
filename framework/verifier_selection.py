"""Verifier selection using ``task_valid_verifiers.csv`` (offline audit from PotARCin).

At runtime, prefer CSV slot order and avoid re-probing every verifier with full
train/test/stable/dynamic50 checks when the CSV lists valid slots. Falls back to
live validation when the CSV is missing or a listed slot has no callable loaded.
"""

from __future__ import annotations

import copy
import csv
import os
from pathlib import Path
from typing import Literal, Optional, Sequence, Tuple

from framework.grids import GridPair, is_equal_grid
from framework.tasks.base import ArcTask, Verifier

VerifierSlot = Literal["re_arc", "google", "keymoon", "neurips", "custom"]

_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_CSV = _ROOT / "task_valid_verifiers.csv"
_CSV_SLOTS: dict[str, list[VerifierSlot]] | None = None
_CSV_LOADED_FROM: Path | None = None

_PRIORITY: tuple[VerifierSlot, ...] = ("re_arc", "google", "keymoon", "neurips", "custom")


def default_verifiers_csv_path() -> Path:
    """CSV path from ``ACTIVEARC_VALID_VERIFIERS_CSV`` or repo-root default."""
    env = os.environ.get("ACTIVEARC_VALID_VERIFIERS_CSV")
    return Path(env).expanduser() if env else _DEFAULT_CSV


def clear_verifier_csv_cache() -> None:
    """Drop cached CSV mapping (e.g. after swapping files in tests)."""
    global _CSV_SLOTS, _CSV_LOADED_FROM
    _CSV_SLOTS = None
    _CSV_LOADED_FROM = None


def _load_csv(path: Path) -> dict[str, list[VerifierSlot]]:
    if not path.is_file():
        return {}
    out: dict[str, list[VerifierSlot]] = {}
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tid = (row.get("task_id") or "").strip()
            if not tid:
                continue
            raw = (row.get("valid_verifier_slots") or "").strip()
            slots: list[VerifierSlot] = []
            for part in raw.split(";"):
                p = part.strip()
                if p in _PRIORITY:
                    slots.append(p)  # type: ignore[arg-type]
            out[tid] = slots
    return out


def csv_slots_for_task(task_id: str, csv_path: Path | None = None) -> list[VerifierSlot]:
    """Return CSV-listed valid slots for *task_id* (empty if unknown or CSV missing)."""
    global _CSV_SLOTS, _CSV_LOADED_FROM
    path = csv_path if csv_path is not None else default_verifiers_csv_path()
    if _CSV_SLOTS is None or _CSV_LOADED_FROM != path:
        _CSV_SLOTS = _load_csv(path)
        _CSV_LOADED_FROM = path
    return _CSV_SLOTS.get(task_id, [])


def eligible_task_ids_from_csv(csv_path: Path | None = None) -> list[str]:
    """Task ids with ≥1 CSV-listed valid verifier slot (empty if CSV missing)."""
    path = csv_path if csv_path is not None else default_verifiers_csv_path()
    if not path.is_file():
        return []
    return [tid for tid, slots in _load_csv(path).items() if slots]


def _callable_for_slot(task: ArcTask, slot: VerifierSlot) -> Verifier | None:
    if slot == "re_arc":
        return task.verifier
    if slot == "google":
        return task.secondary_verifier
    if slot == "keymoon":
        return task.tertiary_verifier
    if slot == "neurips":
        return task.quaternary_verifier
    if slot == "custom":
        return task.quinary_verifier
    return None


def verifier_matches_pairs(v: Verifier, pairs: Sequence[GridPair]) -> bool:
    """True if *v* agrees with every (input, output) pair (safe w.r.t. verifier errors)."""
    for p in pairs:
        try:
            out = v(copy.deepcopy(p.input))
            if not is_equal_grid(out, p.output):
                return False
        except Exception:
            return False
    return True


def list_valid_verifiers_from_csv(
    task: ArcTask,
    *,
    csv_path: Path | None = None,
) -> list[tuple[VerifierSlot, Verifier]] | None:
    """Return CSV-trusted verifiers with callables loaded, or ``None`` if CSV unavailable.

    Skips expensive train/test/stable/dynamic50 re-validation (offline audit in CSV).
    """
    path = csv_path if csv_path is not None else default_verifiers_csv_path()
    if not path.is_file():
        return None
    global _CSV_SLOTS, _CSV_LOADED_FROM
    if _CSV_SLOTS is None or _CSV_LOADED_FROM != path:
        _CSV_SLOTS = _load_csv(path)
        _CSV_LOADED_FROM = path
    if task.task_id not in _CSV_SLOTS:
        return None
    slots = _CSV_SLOTS[task.task_id]
    if not slots:
        return []
    from framework.tasks.arc_dataset import ensure_verifier_slots

    ensure_verifier_slots(task, slots)
    out: list[tuple[VerifierSlot, Verifier]] = []
    for slot in slots:
        fn = _callable_for_slot(task, slot)
        if fn is not None:
            out.append((slot, fn))
    return out


def _legacy_select_verifier(
    task: ArcTask,
    dynamic_pairs: Sequence[GridPair] | None,
) -> Tuple[VerifierSlot, Verifier] | None:
    from framework.dimensions.classification_distribution import (
        verifier_matches_train_test_stable_dynamic50,
    )

    for slot in _PRIORITY:
        fn = _callable_for_slot(task, slot)
        if fn is None:
            continue
        if not verifier_matches_train_test_stable_dynamic50(task, fn):
            continue
        if dynamic_pairs and not verifier_matches_pairs(fn, dynamic_pairs):
            continue
        return slot, fn
    return None


def select_verifier_for_task(
    task: ArcTask,
    *,
    dynamic_pairs: Sequence[GridPair] | None = None,
    csv_path: Path | None = None,
) -> Tuple[VerifierSlot, Verifier] | None:
    """Choose a verifier: CSV ordering first, optional instance dynamic check, then legacy probe."""
    from framework.tasks.arc_dataset import ensure_verifier_slots

    csv_order = csv_slots_for_task(task.task_id, csv_path)
    if csv_order:
        ensure_verifier_slots(task, csv_order)
    for slot in csv_order:
        fn = _callable_for_slot(task, slot)
        if fn is None:
            continue
        if dynamic_pairs and not verifier_matches_pairs(fn, dynamic_pairs):
            continue
        return slot, fn
    return _legacy_select_verifier(task, dynamic_pairs)


def _legacy_valid_verifiers(task: ArcTask) -> list[Tuple[VerifierSlot, Verifier]]:
    from framework.dimensions.classification_distribution import (
        verifier_matches_train_test_stable_dynamic50,
    )
    from framework.tasks.arc_dataset import ensure_alternative_verifiers

    ensure_alternative_verifiers(task)
    out: list[Tuple[VerifierSlot, Verifier]] = []
    for slot in _PRIORITY:
        fn = _callable_for_slot(task, slot)
        if fn is None:
            continue
        if not verifier_matches_train_test_stable_dynamic50(task, fn):
            continue
        out.append((slot, fn))
    return out


def valid_verifiers_for_task(
    task: ArcTask,
    *,
    csv_path: Path | None = None,
) -> list[Tuple[VerifierSlot, Verifier]]:
    """Return all valid verifiers (CSV fast path when available)."""
    fast = list_valid_verifiers_from_csv(task, csv_path=csv_path)
    if fast is not None:
        return fast
    return _legacy_valid_verifiers(task)
