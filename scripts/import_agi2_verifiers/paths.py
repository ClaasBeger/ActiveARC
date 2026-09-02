"""Shared paths for ARC-AGI-2 verifier import."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXTERNAL = ROOT / "external"
SOURCES = EXTERNAL / "agi2_verifier_sources"
OUT = EXTERNAL / "agi2_verifiers"
CANDIDATES = OUT / "candidates"
VALID = OUT / "valid"
LOGS = OUT / "logs"
ARC_ORIGINAL = EXTERNAL / "arc_original_train"
ARC_GEN_V2 = EXTERNAL / "ARC-GEN" / "tasks" / "v2"

GITMONSTERS = SOURCES / "SOLVED-562-verified"
ARUN = SOURCES / "arc-agi2-solutions"
CTPANG = SOURCES / "arc_agi"
CTPANG_PICKLE = CTPANG / "saved_library_1000.pkl"
