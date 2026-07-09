"""ConceptARC integration for ActiveARC.

This adapter exposes ConceptARC DSL programs (exported under
``external/conceptarc/programs``) as ActiveARC :class:`~framework.tasks.base.ArcTask`
objects, kept entirely separate from the ARC-AGI task pool.

Each exported program file carries the serialized DSL program plus three frozen
``train`` examples. The live verifier and the dynamic example generator are
rebuilt from the program using the ConceptARC-GEN package (``conceptarc_gen``),
which is imported live from a configurable location:

* ``CONCEPTARC_GEN_ROOT`` environment variable, if set; otherwise
* the sibling checkout ``../../ConceptARC-Generator/ConceptARC-GEN``; otherwise
* a vendored copy at ``external/ConceptARC-GEN``.

The ConceptARC DSL depends on ARC-GEN's ``common`` module. ConceptARC-GEN pins
its own ARC-GEN checkout (``<gen_root>/external/ARC-GEN``); we import the DSL
stack with that ``common`` on the path and then restore any previously imported
``common`` so ActiveARC's own ARC-GEN path (used by the ARC-AGI dataset) is
unaffected.
"""

from __future__ import annotations

import json
import os
import sys
import threading
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from framework.grids import Grid, GridPair
from framework.tasks.base import ArcTask

_ACTIVEARC_ROOT = Path(__file__).resolve().parents[2]
PROGRAMS_DIR = _ACTIVEARC_ROOT / "external" / "conceptarc" / "programs"

# Concept name -> ConceptARC-GEN generator module attribute name.
_CONCEPT_MODULES: Dict[str, str] = {
    "count": "count_dsl",
    "center": "center_dsl",
    "insideoutside": "inside_outside_dsl",
    "abovebelow": "above_below_dsl",
    "copy": "copy_dsl",
}

_IMPORT_LOCK = threading.Lock()
_GEN_API: Optional["_ConceptArcGenApi"] = None


class _ConceptArcGenApi:
    """Holds imported ConceptARC-GEN modules and helpers."""

    def __init__(
        self,
        gen_root: Path,
        dsl_program_cls: type,
        modules: Dict[str, Any],
    ) -> None:
        self.gen_root = gen_root
        self._DslProgram = dsl_program_cls
        self._modules = modules

    def module_for(self, concept: str) -> Any:
        try:
            return self._modules[concept]
        except KeyError as exc:
            raise KeyError(f"Unknown ConceptARC concept: {concept}") from exc

    def program_from_dict(self, program: Dict[str, Any]) -> Any:
        return self._DslProgram.from_dict(program)


def _candidate_gen_roots() -> List[Path]:
    roots: List[Path] = []
    env = os.environ.get("CONCEPTARC_GEN_ROOT")
    if env:
        roots.append(Path(env).expanduser())
    # Sibling checkout: /.../SFI/ConceptARC-Generator/ConceptARC-GEN
    sfi_root = _ACTIVEARC_ROOT.parent.parent
    roots.append(sfi_root / "ConceptARC-Generator" / "ConceptARC-GEN")
    # Vendored fallback inside ActiveARC.
    roots.append(_ACTIVEARC_ROOT / "external" / "ConceptARC-GEN")
    return roots


def _resolve_gen_root() -> Optional[Path]:
    for root in _candidate_gen_roots():
        if (root / "conceptarc_gen" / "__init__.py").is_file():
            return root
    return None


def _load_gen_api() -> Optional["_ConceptArcGenApi"]:
    """Import ConceptARC-GEN once, isolating its pinned ``common`` module."""
    global _GEN_API
    if _GEN_API is not None:
        return _GEN_API

    with _IMPORT_LOCK:
        if _GEN_API is not None:
            return _GEN_API

        gen_root = _resolve_gen_root()
        if gen_root is None:
            return None

        arc_gen_dir = gen_root / "external" / "ARC-GEN"

        saved_common = sys.modules.pop("common", None)
        added_paths: List[str] = []
        try:
            for p in (str(arc_gen_dir), str(gen_root)):
                if p not in sys.path:
                    sys.path.insert(0, p)
                    added_paths.append(p)

            # Importing the concept modules pulls in the full DSL stack, so every
            # module that does ``import common`` binds ConceptARC-GEN's pinned
            # ``common`` right now.
            import importlib

            from conceptarc_gen.dsl import DslProgram  # type: ignore

            modules: Dict[str, Any] = {}
            for concept, mod_name in _CONCEPT_MODULES.items():
                modules[concept] = importlib.import_module(
                    f"conceptarc_gen.generators.{mod_name}"
                )

            _GEN_API = _ConceptArcGenApi(gen_root, DslProgram, modules)
        except Exception:
            _GEN_API = None
        finally:
            # Restore ActiveARC's own ``common`` (used by the ARC-AGI ARC-GEN path);
            # the ConceptARC modules already captured their own reference.
            if saved_common is not None:
                sys.modules["common"] = saved_common
            else:
                sys.modules.pop("common", None)

    return _GEN_API


def conceptarc_available() -> bool:
    """True if exported programs and the ConceptARC-GEN package are both present."""
    return PROGRAMS_DIR.is_dir() and _load_gen_api() is not None


def _program_path(task_id: str) -> Optional[Path]:
    """Return the JSON path for a normalized ConceptARC task id (e.g. ``count/count11``)."""
    if "/" in task_id:
        concept, name = task_id.split("/", 1)
        path = PROGRAMS_DIR / concept / f"{name}.json"
        return path if path.is_file() else None
    # Bare task name (e.g. ``count11``): search every concept directory.
    for concept_dir in sorted(PROGRAMS_DIR.iterdir()):
        candidate = concept_dir / f"{task_id}.json"
        if candidate.is_file():
            return candidate
    return None


@lru_cache(maxsize=1)
def list_conceptarc_task_ids() -> tuple[str, ...]:
    """Return all exported ConceptARC task ids, sorted by concept then number."""
    if not PROGRAMS_DIR.is_dir():
        return ()

    def _sort_key(tid: str) -> tuple[str, int, str]:
        concept, name = tid.split("/", 1)
        digits = "".join(ch for ch in name if ch.isdigit())
        return (concept, int(digits) if digits else 0, name)

    ids: List[str] = []
    for concept_dir in PROGRAMS_DIR.iterdir():
        if not concept_dir.is_dir():
            continue
        for path in concept_dir.glob("*.json"):
            ids.append(f"{concept_dir.name}/{path.stem}")
    return tuple(sorted(ids, key=_sort_key))


def _make_verifier(module: Any, program: Any) -> Callable[[Grid], Grid]:
    def verifier(grid: Grid) -> Grid:
        return module.transform(program, grid)

    return verifier


def _make_generator(module: Any, program: Any) -> Callable[[int], List[GridPair]]:
    def generator(num_examples: int) -> List[GridPair]:
        pairs: List[GridPair] = []
        for _ in range(num_examples):
            ex = module.generate_program_example(program)
            pairs.append(GridPair(ex["input"], ex["output"]))
        return pairs

    return generator


def load_conceptarc_task(task_id: str) -> ArcTask:
    """Load a ConceptARC program as an ActiveARC :class:`ArcTask`.

    The verifier is stored in the ``custom`` slot (``quinary_verifier``) and is
    also set as the primary ``verifier`` for convenience. ``arc_gen_generator``
    produces fresh dynamic examples from the DSL program.
    """
    api = _load_gen_api()
    if api is None:
        raise RuntimeError(
            "ConceptARC-GEN package not found. Set CONCEPTARC_GEN_ROOT or place a "
            "checkout at ../../ConceptARC-Generator/ConceptARC-GEN."
        )

    path = _program_path(task_id)
    if path is None:
        raise KeyError(f"Unknown ConceptARC task: {task_id!r}")

    data = json.loads(path.read_text(encoding="utf-8"))
    concept = data["concept"]
    module = api.module_for(concept)
    program = api.program_from_dict(data["program"])

    train_pairs = [
        GridPair(ex["input"], ex["output"]) for ex in data.get("train", [])
    ]
    test_examples = data.get("test", [])
    test_inputs = [ex["input"] for ex in test_examples]
    test_outputs = [ex["output"] for ex in test_examples]

    verifier = _make_verifier(module, program)
    generator = _make_generator(module, program)

    normalized_id = data.get("task_id", f"{concept}/{path.stem}")

    task = ArcTask(
        task_id=normalized_id,
        train_pairs=train_pairs,
        test_inputs=test_inputs,
        test_outputs=test_outputs,
        verifier=verifier,
        quinary_verifier=verifier,
        arc_gen_generator=generator,
    )
    # Mark alternative verifiers as loaded so ActiveARC never tries to fetch
    # golf/re_arc verifiers for a ConceptARC task id.
    task._alts_loaded = True  # type: ignore[attr-defined]
    task._conceptarc = True  # type: ignore[attr-defined]
    task._conceptarc_source = data.get("source", "generated")  # type: ignore[attr-defined]
    return task
