"""Load generator/verifier source and optional natural-language rules for the teacher."""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Set

from framework.active_arc.headless_trial import ActiveArcTrialSession
from framework.corruption.golf_ast import golf_solution_path
from framework.dimensions.classification_distribution import VerifierSlot
from framework.tasks.arc_dataset import ROOT_DIR, _arc_gen_id_to_task_num_and_generator

# Inverse Query on ARC-AGI-1: readable RE-ARC verifier over golf one-liners.
# Generator source is chosen separately (ARC-GEN first, then RE-ARC generate_*).
IQ_ARC_VERIFIER_PREFERENCE: tuple[str, ...] = (
    "re_arc",
    "google",
    "keymoon",
    "neurips",
    "custom",
)

_ARC_GEN_COMMON = ROOT_DIR / "external" / "ARC-GEN" / "common.py"
_RE_ARC_DSL = ROOT_DIR / "external" / "re_arc" / "dsl.py"
_RE_ARC_VERIFIERS = ROOT_DIR / "external" / "re_arc" / "verifiers.py"
_RE_ARC_GENERATORS = ROOT_DIR / "external" / "re_arc" / "generators.py"


@dataclass
class TaskPrograms:
    generator_source: Optional[str]
    generator_label: Optional[str]
    verifier_source: Optional[str]
    verifier_label: Optional[str]
    verifier_slot: VerifierSlot
    nl_rule: Optional[str]
    generator_kind: Optional[str] = None
    verifier_kind: Optional[str] = None


def prefer_readable_arc_verifier(session: ActiveArcTrialSession) -> None:
    """If RE-ARC is a valid slot, use it as the gold verifier for Inverse Query."""
    if session.dataset != "arc":
        return
    by_slot = {slot for slot, _fn in session.valid_verifiers}
    for slot in IQ_ARC_VERIFIER_PREFERENCE:
        if slot in by_slot:
            session.verifier_slot = slot  # type: ignore[assignment]
            return


def _read_text(path: Path) -> Optional[str]:
    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def _index_top_level(source: str) -> Dict[str, str]:
    """Map top-level function/constant names to their source, in file order."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}
    out: Dict[str, str] = {}
    for node in tree.body:
        names: List[str] = []
        if isinstance(node, ast.FunctionDef):
            names = [node.name]
        elif isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names = [node.target.id]
        chunk = ast.get_source_segment(source, node)
        if not chunk or not names:
            continue
        for name in names:
            out[name] = chunk
    return out


@lru_cache(maxsize=8)
def _indexed_file(path_str: str) -> Dict[str, str]:
    text = _read_text(Path(path_str))
    if not text:
        return {}
    return _index_top_level(text)


def _local_def_names(source: str) -> Set[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}


def _referenced_names(source: str) -> Set[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    names: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            names.add(node.id)
        elif (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "common"
        ):
            names.add(node.attr)
    return names


def _bundle_helpers(helper_index: Dict[str, str], seeds: Set[str]) -> Optional[str]:
    needed: Set[str] = set()
    stack = [name for name in seeds if name in helper_index]
    while stack:
        name = stack.pop()
        if name in needed:
            continue
        needed.add(name)
        for ref in _referenced_names(helper_index[name]):
            if ref in helper_index and ref not in needed:
                stack.append(ref)
    chunks = [src for name, src in helper_index.items() if name in needed]
    return "\n\n".join(chunks) if chunks else None


def _with_helpers(
    program: str,
    helpers: Optional[str],
    *,
    helper_header: str,
    program_header: str,
) -> str:
    if helpers:
        return f"{helper_header}\n\n{helpers}\n\n{program_header}\n\n{program}"
    return f"{program_header}\n\n{program}" if program_header else program


def _arc_gen_generator_path(task_id: str) -> Optional[Path]:
    lookup = _arc_gen_id_to_task_num_and_generator(task_id)
    v2 = ROOT_DIR / "external" / "ARC-GEN" / "tasks" / "v2" / f"task_{task_id}.py"
    if v2.is_file():
        return v2
    if lookup is None:
        return None
    task_num, _ = lookup
    v1 = ROOT_DIR / "external" / "ARC-GEN" / "tasks" / "training" / f"task{task_num:03d}.py"
    return v1 if v1.is_file() else None


def _arc_gen_generator_source(task_id: str) -> tuple[Optional[str], Optional[str]]:
    path = _arc_gen_generator_path(task_id)
    raw = _read_text(path) if path is not None else None
    if not raw or path is None:
        return None, None
    helpers = _bundle_helpers(
        _indexed_file(str(_ARC_GEN_COMMON)),
        _referenced_names(raw) - _local_def_names(raw),
    )
    composed = _with_helpers(
        raw,
        helpers,
        helper_header=(
            "# ARC-GEN helpers referenced by this generator "
            f"(from {_ARC_GEN_COMMON}).\n"
            "# Ordinary Python utilities — not the RE-ARC / Michael Hodel DSL."
        ),
        program_header=f"# Generator ({path})",
    )
    return composed, str(path)


def _re_arc_generator_source(task_id: str) -> tuple[Optional[str], Optional[str]]:
    fn = _indexed_file(str(_RE_ARC_GENERATORS)).get(f"generate_{task_id}")
    if not fn:
        return None, None
    helpers = _bundle_helpers(
        _indexed_file(str(_RE_ARC_DSL)),
        _referenced_names(fn) - _local_def_names(fn),
    )
    label = f"re_arc generate_{task_id}"
    composed = _with_helpers(
        fn,
        helpers,
        helper_header=(
            f"# RE-ARC DSL primitives referenced by this generator (from {_RE_ARC_DSL}).\n"
            "# Generators assume `from dsl import *`."
        ),
        program_header=f"# {label}",
    )
    return composed, label


def _re_arc_verifier_source(task_id: str) -> Optional[str]:
    fn = _indexed_file(str(_RE_ARC_VERIFIERS)).get(f"verify_{task_id}")
    if not fn:
        return None
    helpers = _bundle_helpers(
        _indexed_file(str(_RE_ARC_DSL)),
        _referenced_names(fn) - _local_def_names(fn),
    )
    return _with_helpers(
        fn,
        helpers,
        helper_header=(
            f"# RE-ARC DSL primitives referenced by this verifier (from {_RE_ARC_DSL}).\n"
            "# Verifiers assume `from dsl import *`."
        ),
        program_header=f"# re_arc verify_{task_id}",
    )


def _golf_verifier_source(task_id: str, slot: VerifierSlot) -> Optional[str]:
    if slot not in ("google", "keymoon", "neurips"):
        return None
    path = golf_solution_path(task_id, slot)  # type: ignore[arg-type]
    if path is not None:
        return _read_text(path)
    return None


def _custom_verifier_source(session: ActiveArcTrialSession) -> tuple[Optional[str], Optional[str]]:
    dataset = session.dataset
    task_id = session.task_id
    if dataset == "parc":
        from framework.tasks.parc_dataset import parc_source_paths

        _gen, ver = parc_source_paths(task_id)
        return _read_text(ver), str(ver) if ver.is_file() else None
    if dataset == "arc2":
        from framework.integrations.agi2_verifiers import list_agi2_valid_source_paths

        files = list_agi2_valid_source_paths(task_id)
        if not files:
            return None, None
        chunks = []
        labels = []
        for cid, path in files:
            text = _read_text(path)
            if text:
                chunks.append(f"# candidate {cid} ({path.name})\n{text}")
                labels.append(str(path))
        return ("\n\n".join(chunks) if chunks else None), "; ".join(labels) or None
    if dataset == "conceptarc":
        program = getattr(session.task, "_conceptarc_program_json", None)
        if isinstance(program, dict):
            return json.dumps(program, indent=2), "conceptarc DSL program"
        from framework.integrations.conceptarc_adapter import _program_path

        path = _program_path(task_id)
        if path is None:
            return None, None
        data = json.loads(path.read_text(encoding="utf-8"))
        slim = {
            k: data[k]
            for k in ("concept", "description", "program", "program_kind", "task_id")
            if k in data
        }
        return json.dumps(slim, indent=2), str(path)
    return None, None


def _nl_rule(session: ActiveArcTrialSession) -> Optional[str]:
    task = session.task
    concept = session.task_id.split("/", 1)[0] if "/" in session.task_id else None
    if session.dataset == "conceptarc" or getattr(task, "_conceptarc", False):
        from framework.integrations.conceptarc_adapter import conceptarc_ground_truth_rule

        gt = conceptarc_ground_truth_rule(session.task_id)
        if gt:
            return f"Concept: {concept}. {gt}" if concept else gt
        desc = getattr(task, "_conceptarc_description", None)
        if (
            isinstance(desc, str)
            and desc.strip()
            and not desc.strip().startswith("Official ConceptARC")
        ):
            return f"Concept: {concept}. {desc.strip()}" if concept else desc.strip()
        return None
    if session.dataset == "parc":
        from framework.tasks.parc_dataset import parse_parc_task_num, resolve_test2_dir

        root = resolve_test2_dir()
        if root is None:
            return None
        path = root / f"t{parse_parc_task_num(session.task_id)}.json"
        if not path.is_file():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        for key in ("description", "rule", "nl_rule", "natural_language"):
            val = payload.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
    if session.dataset == "arc":
        from framework.integrations.nl_rules import larc_rule

        return larc_rule(session.task_id)
    if session.dataset == "arc2":
        from framework.integrations.nl_rules import marc2_rule

        return marc2_rule(session.task_id)
    return None


def load_task_programs(session: ActiveArcTrialSession) -> TaskPrograms:
    """Collect teacher-facing programs. ARC-GEN generator beats RE-ARC; RE-ARC verifier beats golf."""
    slot = session.verifier_slot
    gen_src: Optional[str] = None
    gen_label: Optional[str] = None
    gen_kind: Optional[str] = None
    ver_src: Optional[str] = None
    ver_label: Optional[str] = None
    ver_kind: Optional[str] = None

    if session.dataset == "parc":
        from framework.tasks.parc_dataset import parc_source_paths

        gen_path, ver_path = parc_source_paths(session.task_id)
        gen_src, gen_label = _read_text(gen_path), str(gen_path)
        ver_src, ver_label = _read_text(ver_path), str(ver_path)
        gen_kind, ver_kind = "parc", "parc"
    elif session.dataset == "conceptarc":
        gen_src, gen_label = _custom_verifier_source(session)
        ver_src, ver_label = gen_src, gen_label
        gen_kind = ver_kind = "conceptarc"
    else:
        gen_src, gen_label = _arc_gen_generator_source(session.task_id)
        if gen_src:
            gen_kind = "arc_gen"
        else:
            gen_src, gen_label = _re_arc_generator_source(session.task_id)
            if gen_src:
                gen_kind = "re_arc"

        if slot == "re_arc":
            ver_src = _re_arc_verifier_source(session.task_id)
            if ver_src:
                ver_label = f"re_arc verify_{session.task_id}"
                ver_kind = "re_arc"
        elif slot in ("google", "keymoon", "neurips"):
            ver_src = _golf_verifier_source(session.task_id, slot)
            path = golf_solution_path(session.task_id, slot)  # type: ignore[arg-type]
            ver_label = str(path) if path is not None else slot
            ver_kind = slot
        if ver_src is None:
            ver_src, ver_label = _custom_verifier_source(session)
            if ver_src:
                ver_kind = "custom"

    return TaskPrograms(
        generator_source=gen_src,
        generator_label=gen_label,
        verifier_source=ver_src,
        verifier_label=ver_label,
        verifier_slot=slot,
        nl_rule=_nl_rule(session),
        generator_kind=gen_kind,
        verifier_kind=ver_kind,
    )
