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

In addition to loading frozen exports, :func:`sample_conceptarc_task` can invent
a new DSL task family online (ConceptARC-GEN layer 3) for a chosen concept.
"""

from __future__ import annotations

import json
import os
import random
import sys
import threading
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from framework.grids import Grid, GridPair
from framework.tasks.base import ArcTask

_ACTIVEARC_ROOT = Path(__file__).resolve().parents[2]
PROGRAMS_DIR = _ACTIVEARC_ROOT / "external" / "conceptarc" / "programs"
_SAMPLE_TRAIN = 3
_SAMPLE_TEST = 3
_SAMPLE_ATTEMPTS = 400

# Concept name -> ConceptARC-GEN generator module attribute name.
# Keep in sync with ConceptARC-GEN ``registry.concept_groups`` / ``export_to_activearc.CONCEPTS``.
_CONCEPT_MODULES: Dict[str, str] = {
    "count": "count_dsl",
    "center": "center_dsl",
    "insideoutside": "inside_outside_dsl",
    "abovebelow": "above_below_dsl",
    "topbottom2d": "top_bottom_2d_dsl",
    "topbottom3d": "top_bottom_3d_dsl",
    "copy": "copy_dsl",
    "extendtoboundary": "extend_to_boundary_dsl",
    "extract": "extract_dsl",
    "movetoboundary": "move_to_boundary_dsl",
    "order": "order_dsl",
    "samedifferent": "same_different_dsl",
    "completeshape": "complete_shape_dsl",
    "cleanup": "cleanup_dsl",
    "fillednotfilled": "filled_not_filled_dsl",
    "horizontalvertical": "horizontal_vertical_dsl",
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
        generate_task_family_specs: Callable[..., List[Any]],
        save_task_family_spec: Callable[..., Path],
        default_spec_dir: Path,
    ) -> None:
        self.gen_root = gen_root
        self._DslProgram = dsl_program_cls
        self._modules = modules
        self._generate_task_family_specs = generate_task_family_specs
        self._save_task_family_spec = save_task_family_spec
        self.default_spec_dir = default_spec_dir

    def module_for(self, concept: str) -> Any:
        try:
            return self._modules[concept]
        except KeyError as exc:
            raise KeyError(f"Unknown ConceptARC concept: {concept}") from exc

    def program_from_dict(self, program: Dict[str, Any]) -> Any:
        return self._DslProgram.from_dict(program)

    def sample_family_spec(self, concept: str, seed: int) -> Any:
        """Sample one new task-family spec (not written unless caller persists)."""
        specs = self._generate_task_family_specs(
            concept,
            1,
            seed,
            self.default_spec_dir,
        )
        if not specs:
            raise RuntimeError(f"No task-family spec sampled for concept {concept!r}")
        return specs[0]


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
            from conceptarc_gen.task_families import (  # type: ignore
                DEFAULT_SPEC_DIR,
                save_task_family_spec,
            )
            from conceptarc_gen_tasks import generate_task_family_specs  # type: ignore

            modules: Dict[str, Any] = {}
            for concept, mod_name in _CONCEPT_MODULES.items():
                modules[concept] = importlib.import_module(
                    f"conceptarc_gen.generators.{mod_name}"
                )

            spec_dir = Path(DEFAULT_SPEC_DIR)
            if not spec_dir.is_absolute():
                spec_dir = gen_root / spec_dir

            _GEN_API = _ConceptArcGenApi(
                gen_root,
                DslProgram,
                modules,
                generate_task_family_specs,
                save_task_family_spec,
                spec_dir,
            )
        except Exception as exc:
            import warnings

            warnings.warn(
                f"Failed to import ConceptARC-GEN from {gen_root}: {type(exc).__name__}: {exc}",
                RuntimeWarning,
                stacklevel=2,
            )
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


def list_conceptarc_concepts() -> tuple[str, ...]:
    """Return supported ConceptARC concept names."""
    return tuple(sorted(_CONCEPT_MODULES))


def is_conceptarc_sample_request(task_id: Optional[str]) -> bool:
    """True when ``task_id`` asks to sample a new DSL family online.

    Accepted forms: ``sample``, ``sample/<concept>``, ``<concept>/sample``.
    """
    if task_id is None:
        return False
    tid = task_id.strip().lower()
    if tid == "sample":
        return True
    if "/" not in tid:
        return False
    left, right = tid.split("/", 1)
    return left == "sample" or right == "sample"


def concept_from_sample_request(task_id: str) -> Optional[str]:
    """Return a pinned concept from a sample request, or ``None`` to pick randomly."""
    tid = task_id.strip().lower()
    if tid == "sample":
        return None
    left, right = tid.split("/", 1)
    if left == "sample":
        concept = right
    elif right == "sample":
        concept = left
    else:
        return None
    if concept not in _CONCEPT_MODULES:
        raise KeyError(f"Unknown ConceptARC concept in sample request: {concept!r}")
    return concept


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


def _grid_key(grid: Grid) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(int(c) for c in row) for row in grid)


def _generate_examples(
    module: Any,
    program: Any,
    seed: int,
    count: int,
    *,
    required: bool,
) -> List[dict]:
    """Generate up to ``count`` distinct examples from a DSL program."""
    random.seed(seed)
    out: List[dict] = []
    seen: set[tuple[Any, Any]] = set()
    attempts = 0
    while len(out) < count and attempts < _SAMPLE_ATTEMPTS:
        attempts += 1
        try:
            ex = module.generate_program_example(program)
        except Exception:
            continue
        key = (_grid_key(ex["input"]), _grid_key(ex["output"]))
        if key in seen:
            continue
        seen.add(key)
        out.append({"input": ex["input"], "output": ex["output"]})
    if required and len(out) < count:
        raise RuntimeError(
            f"Could only generate {len(out)}/{count} distinct ConceptARC examples."
        )
    return out


def _arc_task_from_payload(
    *,
    task_id: str,
    concept: str,
    program: Any,
    module: Any,
    train: List[dict],
    test: List[dict],
    source: str,
    description: str = "",
) -> ArcTask:
    verifier = _make_verifier(module, program)
    generator = _make_generator(module, program)
    task = ArcTask(
        task_id=task_id,
        train_pairs=[GridPair(ex["input"], ex["output"]) for ex in train],
        test_inputs=[ex["input"] for ex in test],
        test_outputs=[ex["output"] for ex in test],
        verifier=verifier,
        quinary_verifier=verifier,
        arc_gen_generator=generator,
    )
    # Mark alternative verifiers as loaded so ActiveARC never tries to fetch
    # golf/re_arc verifiers for a ConceptARC task id.
    task._alts_loaded = True  # type: ignore[attr-defined]
    task._conceptarc = True  # type: ignore[attr-defined]
    task._conceptarc_source = source  # type: ignore[attr-defined]
    task._conceptarc_description = description  # type: ignore[attr-defined]
    return task


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
    normalized_id = data.get("task_id", f"{concept}/{path.stem}")
    return _arc_task_from_payload(
        task_id=normalized_id,
        concept=concept,
        program=program,
        module=module,
        train=list(data.get("train", [])),
        test=list(data.get("test", [])),
        source=str(data.get("source", "generated")),
        description=str(data.get("description", "")),
    )


def sample_conceptarc_task(
    *,
    concept: Optional[str] = None,
    seed: int,
    n_train: int = _SAMPLE_TRAIN,
    n_test: int = _SAMPLE_TEST,
    persist: bool = False,
) -> ArcTask:
    """Sample a new ConceptARC DSL task family and return it as an :class:`ArcTask`.

    This is ConceptARC-GEN layer 3 (new program), then layer 1 example sampling for
    frozen train/test pools. The resulting task still exposes
    ``arc_gen_generator`` for further live pairs.

    Args:
      concept: Concept to sample; ``None`` picks uniformly from
          :func:`list_conceptarc_concepts`.
      seed: Base seed for family sampling and example generation.
      n_train: Number of distinct train examples to freeze.
      n_test: Number of distinct held-out test examples (best-effort).
      persist: When true, write the family spec under ConceptARC-GEN's
          ``output/conceptarc_specs`` and an ActiveARC program JSON under
          :data:`PROGRAMS_DIR`, and clear the task-id cache.
    """
    api = _load_gen_api()
    if api is None:
        raise RuntimeError(
            "ConceptARC-GEN package not found. Set CONCEPTARC_GEN_ROOT or place a "
            "checkout at ../../ConceptARC-Generator/ConceptARC-GEN."
        )

    concepts = list(list_conceptarc_concepts())
    if concept is None:
        concept = concepts[seed % len(concepts)]
    elif concept not in _CONCEPT_MODULES:
        raise KeyError(f"Unknown ConceptARC concept: {concept!r}")

    spec = api.sample_family_spec(concept, seed)
    module = api.module_for(concept)
    if not module.is_valid_generated_spec(spec):
        raise RuntimeError(
            f"Sampled ConceptARC spec {spec.task_id!r} failed concept validation."
        )
    program = api.program_from_dict(spec.program)

    train = _generate_examples(module, program, seed + 17, n_train, required=True)
    test = _generate_examples(module, program, seed + 9973, n_test, required=False)
    train_keys = {(_grid_key(e["input"]), _grid_key(e["output"])) for e in train}
    test = [
        e
        for e in test
        if (_grid_key(e["input"]), _grid_key(e["output"])) not in train_keys
    ]

    # Ephemeral ids stay stable for the trial seed without colliding with exports.
    prefix = concept
    for name in dir(module):
        if name.endswith("_DSL_PROFILE"):
            profile = getattr(module, name)
            prefix = getattr(profile, "task_name_prefix", concept)
            break
    task_id = f"{concept}/{prefix}_s{seed}"

    if persist:
        api._save_task_family_spec(spec, api.default_spec_dir)
        name = spec.task_id.split("/")[-1]
        payload = {
            "task_id": spec.task_id,
            "concept": concept,
            "source": "generated",
            "program_kind": spec.program_kind,
            "description": spec.description,
            "program": spec.program,
            "train": train,
            "test": test,
        }
        out_path = PROGRAMS_DIR / concept / f"{name}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
        )
        list_conceptarc_task_ids.cache_clear()
        task_id = spec.task_id

    return _arc_task_from_payload(
        task_id=task_id,
        concept=concept,
        program=program,
        module=module,
        train=train,
        test=test,
        source="sampled" if not persist else "generated",
        description=str(spec.description),
    )