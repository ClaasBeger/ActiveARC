"""Load validated ARC-AGI-2 standalone verifiers from ``external/agi2_verifiers/valid``."""

from __future__ import annotations

import importlib.util
import json
from functools import lru_cache
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from framework.tasks.base import Grid

ROOT_DIR = Path(__file__).resolve().parents[2]
VALID_DIR = ROOT_DIR / "external" / "agi2_verifiers" / "valid"

Verifier = Callable[[Grid], Grid]


def _load_verify(path: Path) -> Optional[Verifier]:
    try:
        spec = importlib.util.spec_from_file_location(f"agi2_valid_{path.stem}", path)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fn = getattr(mod, "verify", None)
        if not callable(fn):
            return None

        def _verify(input_grid, _fn=fn):
            got = _fn(input_grid)
            if hasattr(got, "tolist"):
                got = got.tolist()
            return [[int(c) for c in row] for row in got]

        return _verify
    except Exception:
        return None


@lru_cache(maxsize=1)
def _index() -> Dict[str, List[Tuple[str, Path]]]:
    """task_id -> [(candidate_id, path), ...]"""
    out: Dict[str, List[Tuple[str, Path]]] = {}
    if not VALID_DIR.is_dir():
        return out
    for py in sorted(VALID_DIR.glob("*/*.py")):
        meta_path = py.with_suffix(py.suffix + ".meta.json")
        cid = py.stem
        if meta_path.is_file():
            try:
                cid = json.loads(meta_path.read_text()).get("candidate_id", cid)
            except Exception:
                pass
        out.setdefault(py.parent.name, []).append((cid, py))
    return out


def clear_agi2_verifier_cache() -> None:
    _index.cache_clear()


def list_agi2_valid_task_ids() -> List[str]:
    """Task ids with ≥1 promoted valid AGI-2 verifier."""
    return sorted(_index())


def list_agi2_valid_candidate_ids(task_id: str) -> List[str]:
    return [cid for cid, _ in _index().get(task_id, [])]


def get_agi2_valid_verifiers(task_id: str) -> List[Tuple[str, Verifier]]:
    """Return all validated AGI-2 verifier callables for *task_id*."""
    loaded: List[Tuple[str, Verifier]] = []
    for cid, path in _index().get(task_id, []):
        fn = _load_verify(path)
        if fn is not None:
            loaded.append((cid, fn))
    return loaded


def get_agi2_valid_verifier(task_id: str) -> Optional[Verifier]:
    """First validated AGI-2 verifier for *task_id*, if any."""
    items = get_agi2_valid_verifiers(task_id)
    return items[0][1] if items else None
