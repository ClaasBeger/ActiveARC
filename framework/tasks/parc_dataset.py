"""P-ARC (PotARCin Test2) task loading for ActiveARC.

P-ARC is the fifty-task Test2 set from PotARCin (``t1``–``t50``). Each task has:

* ``Test2/t<n>.json`` — train/test demonstrations
* ``Test2/t<n>_*/verifier.py`` — ground-truth transform
* ``Test2/t<n>_*/generator.py`` — live example sampler
* ``Test2/t<n>_*/t<n>_samples_50.json`` — committed 50-pair stable pool

Data is resolved from (first hit wins):

* ``PARC_ROOT`` or ``TEST2_DIR`` environment variable
* ``external/Test2`` under the ActiveARC checkout
* sibling ``../../PotARCin/PotARCin/Test2``
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import os
import re
import sys
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Callable, Iterator, List, Optional

from framework.grids import Grid, GridPair
from framework.tasks.base import ArcTask

_ACTIVEARC_ROOT = Path(__file__).resolve().parents[2]

_TASK_DIR_CACHE: dict[int, Path] | None = None
_VERIFIER_CACHE: dict[int, Callable[[Grid], Grid]] = {}
_GENERATOR_CACHE: dict[int, Callable[[int], List[GridPair]]] = {}
_TEST2_DIR: Optional[Path] = None
_TEST2_RESOLVED = False


def _candidate_test2_dirs() -> List[Path]:
    roots: List[Path] = []
    for env in ("PARC_ROOT", "TEST2_DIR"):
        raw = os.environ.get(env)
        if raw:
            p = Path(raw).expanduser()
            # Allow pointing at either Test2 itself or the PotARCin repo root.
            roots.append(p if p.name == "Test2" or (p / "t1.json").is_file() else p / "Test2")
    roots.append(_ACTIVEARC_ROOT / "external" / "Test2")
    roots.append(_ACTIVEARC_ROOT / "external" / "p_arc" / "Test2")
    # Sibling: /.../SFI/PotARCin/PotARCin/Test2
    sfi = _ACTIVEARC_ROOT.parent.parent
    roots.append(sfi / "PotARCin" / "PotARCin" / "Test2")
    return roots


def resolve_test2_dir() -> Optional[Path]:
    """Return the Test2 root if available, else ``None``."""
    global _TEST2_DIR, _TEST2_RESOLVED
    if _TEST2_RESOLVED:
        return _TEST2_DIR
    for root in _candidate_test2_dirs():
        if root.is_dir() and (root / "t1.json").is_file():
            _TEST2_DIR = root
            _TEST2_RESOLVED = True
            return root
    _TEST2_DIR = None
    _TEST2_RESOLVED = True
    return None


def parc_available() -> bool:
    """True when the P-ARC Test2 tree is resolvable."""
    return resolve_test2_dir() is not None


def _is_int_grid(grid: object) -> bool:
    if not isinstance(grid, list) or not grid:
        return False
    if not all(isinstance(row, list) and row for row in grid):
        return False
    width = len(grid[0])
    if width == 0 or any(len(row) != width for row in grid):
        return False
    for row in grid:
        for cell in row:
            if type(cell) is not int or cell < 0 or cell > 9:
                return False
    return True


def parse_parc_task_num(task_id: str) -> int:
    s = task_id.strip().lower()
    for pat in (r"test2_t(\d+)", r"parc_t(\d+)", r"p-?arc_t(\d+)", r"t(\d+)"):
        m = re.fullmatch(pat, s)
        if m:
            n = int(m.group(1))
            if 1 <= n <= 50:
                return n
    raise ValueError(f"Invalid P-ARC task id: {task_id!r}")


def canonical_parc_task_id(task_id: str) -> str:
    return f"test2_t{parse_parc_task_num(task_id)}"


def _discover_task_dirs(test2_dir: Path) -> dict[int, Path]:
    global _TASK_DIR_CACHE
    if _TASK_DIR_CACHE is not None:
        return _TASK_DIR_CACHE
    mapping: dict[int, Path] = {}
    for p in sorted(test2_dir.iterdir()):
        if not p.is_dir():
            continue
        m = re.match(r"t(\d+)_", p.name)
        if not m:
            continue
        n = int(m.group(1))
        if 1 <= n <= 50 and n not in mapping:
            mapping[n] = p
    _TASK_DIR_CACHE = mapping
    return mapping


def _task_dir(task_num: int) -> Path:
    test2_dir = resolve_test2_dir()
    if test2_dir is None:
        raise FileNotFoundError(
            "P-ARC Test2 data not found. Set PARC_ROOT/TEST2_DIR or place Test2 under "
            "external/Test2 (or keep the sibling PotARCin/PotARCin/Test2 checkout)."
        )
    mapping = _discover_task_dirs(test2_dir)
    if task_num not in mapping:
        raise FileNotFoundError(
            f"Missing Test2 subdirectory for t{task_num} under {test2_dir}"
        )
    return mapping[task_num]


def _load_module(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    old_path = list(sys.path)
    old_generator_module = sys.modules.pop("generator", None)
    old_verifier_module = sys.modules.pop("verifier", None)
    try:
        task_dir = str(path.parent)
        if task_dir not in sys.path:
            sys.path.insert(0, task_dir)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path = old_path
        if old_generator_module is not None:
            sys.modules["generator"] = old_generator_module
        else:
            sys.modules.pop("generator", None)
        if old_verifier_module is not None:
            sys.modules["verifier"] = old_verifier_module
        else:
            sys.modules.pop("verifier", None)


def _wrap_verifier_fn(fn: Callable[..., object], task_num: int) -> Callable[[Grid], Grid]:
    sig = inspect.signature(fn)
    required = [
        p
        for p in sig.parameters.values()
        if p.default is inspect._empty
        and p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    arity = len(required)
    if arity == 1:

        def _one_arg(grid: Grid) -> Grid:
            out = fn(grid)  # type: ignore[misc]
            if not _is_int_grid(out):
                raise ValueError(f"P-ARC verifier verify_t{task_num} returned non-grid output")
            return out  # type: ignore[return-value]

        return _one_arg
    raise ValueError(
        f"Unsupported verifier signature for t{task_num}: expected one required arg, got {arity}"
    )


def _load_parc_verifier(task_num: int) -> Optional[Callable[[Grid], Grid]]:
    if task_num in _VERIFIER_CACHE:
        return _VERIFIER_CACHE[task_num]
    path = _task_dir(task_num) / "verifier.py"
    if not path.is_file():
        return None
    module = _load_module(path, f"parc_verifier_t{task_num}")
    candidates = (
        f"verify_t{task_num}",
        f"transform_t{task_num}",
        "verify",
        "transform",
    )
    for name in candidates:
        raw = getattr(module, name, None)
        if callable(raw):
            try:
                wrapped = _wrap_verifier_fn(raw, task_num)
            except Exception:
                continue
            _VERIFIER_CACHE[task_num] = wrapped
            return wrapped
    verify_bool = getattr(module, f"verify_t{task_num}", None)
    transform = getattr(module, f"transform_t{task_num}", None)
    if callable(verify_bool) and callable(transform):
        try:
            verify_sig = inspect.signature(verify_bool)
            if (
                len(
                    [
                        p
                        for p in verify_sig.parameters.values()
                        if p.default is inspect._empty
                        and p.kind
                        in (
                            inspect.Parameter.POSITIONAL_ONLY,
                            inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        )
                    ]
                )
                == 2
            ):
                wrapped = _wrap_verifier_fn(transform, task_num)
                _VERIFIER_CACHE[task_num] = wrapped
                return wrapped
        except Exception:
            pass
    return None


def _load_parc_generator(task_num: int) -> Optional[Callable[[int], List[GridPair]]]:
    if task_num in _GENERATOR_CACHE:
        return _GENERATOR_CACHE[task_num]
    path = _task_dir(task_num) / "generator.py"
    if not path.is_file():
        return None
    module = _load_module(path, f"parc_generator_t{task_num}")
    raw = getattr(module, "generate", None)
    if not callable(raw):
        return None
    task_dir = _task_dir(task_num)
    verifier_path = task_dir / "verifier.py"

    def _gen(num_examples: int) -> List[GridPair]:
        out: List[GridPair] = []
        for _ in range(num_examples):
            old_path = list(sys.path)
            old_verifier_module = sys.modules.pop("verifier", None)
            try:
                p = str(task_dir)
                if p not in sys.path:
                    sys.path.insert(0, p)
                if verifier_path.is_file():
                    sys.modules["verifier"] = _load_module(
                        verifier_path, f"parc_runtime_verifier_t{task_num}"
                    )
                try:
                    sample = raw(rng=None)
                except TypeError:
                    sample = raw()
            finally:
                sys.path = old_path
                if old_verifier_module is not None:
                    sys.modules["verifier"] = old_verifier_module
                else:
                    sys.modules.pop("verifier", None)
            if not isinstance(sample, dict):
                raise ValueError(f"P-ARC generator t{task_num} returned non-dict sample")
            inp = sample.get("input")
            output = sample.get("output")
            if not _is_int_grid(inp) or not _is_int_grid(output):
                raise ValueError(f"P-ARC generator t{task_num} returned invalid grids")
            out.append(GridPair(inp, output))  # type: ignore[arg-type]
        return out

    _GENERATOR_CACHE[task_num] = _gen
    return _gen


def _load_parc_stable_pairs(task_num: int) -> List[GridPair]:
    """Load ``t<n>_samples_50.json`` ``train`` array (committed stable pool)."""
    td = _task_dir(task_num)
    path = td / f"t{task_num}_samples_50.json"
    if not path.is_file():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    train = payload.get("train")
    if not isinstance(train, list):
        return []
    out: List[GridPair] = []
    for i, ex in enumerate(train):
        if not isinstance(ex, dict):
            continue
        inp, outg = ex.get("input"), ex.get("output")
        if not _is_int_grid(inp) or not _is_int_grid(outg):
            raise ValueError(f"{path}: invalid train[{i}] grid(s)")
        out.append(GridPair(inp, outg))  # type: ignore[arg-type]
    return out


@lru_cache(maxsize=1)
def list_parc_task_ids() -> tuple[str, ...]:
    """Return canonical ids for every resolvable P-ARC task (``test2_t1`` …)."""
    if not parc_available():
        return ()
    test2_dir = resolve_test2_dir()
    assert test2_dir is not None
    mapping = _discover_task_dirs(test2_dir)
    ids: List[str] = []
    for n in range(1, 51):
        if n in mapping and (test2_dir / f"t{n}.json").is_file():
            ids.append(f"test2_t{n}")
    return tuple(ids)


def load_parc_task(task_id: str) -> ArcTask:
    """Load a P-ARC Test2 task as an ActiveARC :class:`ArcTask`."""
    task_num = parse_parc_task_num(task_id)
    test2_dir = resolve_test2_dir()
    if test2_dir is None:
        raise FileNotFoundError("P-ARC Test2 data not found.")
    task_json = test2_dir / f"t{task_num}.json"
    if not task_json.is_file():
        raise FileNotFoundError(f"Missing P-ARC task file: {task_json}")
    payload = json.loads(task_json.read_text(encoding="utf-8"))
    train = payload.get("train")
    test = payload.get("test")
    if not isinstance(train, list) or not isinstance(test, list):
        raise ValueError(f"Malformed P-ARC task JSON: {task_json}")

    train_pairs: List[GridPair] = []
    for i, ex in enumerate(train):
        if not isinstance(ex, dict):
            raise ValueError(f"{task_json}: train[{i}] must be an object")
        inp, out = ex.get("input"), ex.get("output")
        if not _is_int_grid(inp) or not _is_int_grid(out):
            raise ValueError(f"{task_json}: invalid train[{i}] grid(s)")
        train_pairs.append(GridPair(inp, out))  # type: ignore[arg-type]

    test_inputs: List[Grid] = []
    test_outputs: List[Grid] = []
    for i, ex in enumerate(test):
        if not isinstance(ex, dict):
            raise ValueError(f"{task_json}: test[{i}] must be an object")
        inp, out = ex.get("input"), ex.get("output")
        if not _is_int_grid(inp) or not _is_int_grid(out):
            raise ValueError(f"{task_json}: invalid test[{i}] grid(s)")
        test_inputs.append(inp)  # type: ignore[arg-type]
        test_outputs.append(out)  # type: ignore[arg-type]

    verifier = _load_parc_verifier(task_num)
    generator = _load_parc_generator(task_num)
    stable = _load_parc_stable_pairs(task_num)

    task = ArcTask(
        task_id=canonical_parc_task_id(task_id),
        train_pairs=train_pairs,
        test_inputs=test_inputs,
        test_outputs=test_outputs,
        verifier=verifier,
        quinary_verifier=verifier,
        arc_gen_generator=generator,
        p_arc_stable_pairs=stable,
    )
    task._alts_loaded = True  # type: ignore[attr-defined]
    task._parc = True  # type: ignore[attr-defined]
    return task


def iter_parc_tasks() -> Iterator[ArcTask]:
    for tid in list_parc_task_ids():
        yield load_parc_task(tid)
