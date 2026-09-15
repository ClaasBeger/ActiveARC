"""Load generator/verifier source and optional natural-language rules for the teacher."""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from framework.active_arc.headless_trial import ActiveArcTrialSession
from framework.corruption.golf_ast import golf_solution_path
from framework.dimensions.classification_distribution import VerifierSlot
from framework.tasks.arc_dataset import ROOT_DIR, _arc_gen_id_to_task_num_and_generator

# Kept for callers that still import it. The teacher is no longer handed a
# verifier chosen for readability: the gold oracle is whatever ``pick_verifier``
# pinned -- the task's canonical slot -- and the source shown is that slot's.
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
    nl_rule_source: Optional[str] = None
    # ConceptARC only: the DSL descriptor itself, shown as a JSON object beside
    # the bundled interpreter source.
    verifier_program_json: Optional[Dict[str, Any]] = None


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
    if slot == "keymoon":
        # Same fallback as the runtime loader: the bundled snapshot ships the
        # solutions inside submission.zip rather than as files under sols/.
        import zipfile

        from framework.tasks.arc_dataset import _arc_gen_id_to_task_num_and_generator

        lookup = _arc_gen_id_to_task_num_and_generator(task_id)
        zip_path = ROOT_DIR / "external" / "golf" / "submission.zip"
        if lookup is not None and zip_path.is_file():
            task_num, _ = lookup
            try:
                with zipfile.ZipFile(zip_path) as zf:
                    raw = zf.read(f"task{task_num:03d}.py")
            except (KeyError, zipfile.BadZipFile, OSError):
                return None
            for enc in ("utf-8", "cp1252", "latin-1"):
                try:
                    return raw.decode(enc)
                except UnicodeDecodeError:
                    continue
    return None


def _parc_verifier_source(task_id: str) -> tuple[Optional[str], Optional[str]]:
    """The P-ARC verifier with the rule it delegates to.

    Most ``verifier.py`` files are a 19-line wrapper: ``from generator import
    transform_tNN`` plus a shape check. The rule lives in ``transform_tNN`` in
    ``generator.py``, so that function and the helpers it reaches are bundled
    ahead of the wrapper, RE-ARC style. The sampling side of ``generator.py``
    (``generate*``) is not referenced by any transform and is never included.
    Nine tasks have a self-contained ``verifier.py``; those go in as they are.
    """
    import re as _re

    from framework.tasks.parc_dataset import parc_source_paths

    gen_path, ver_path = parc_source_paths(task_id)
    ver_src = _read_text(ver_path)
    if not ver_src:
        return None, None
    label = str(ver_path)
    m = _re.search(r"^from generator import ([\w, ]+)$", ver_src, _re.M)
    if not m:
        return ver_src, label
    names = {n.strip() for n in m.group(1).split(",") if n.strip()}
    gen_src = _read_text(gen_path) or ""
    index = {k: v for k, v in _index_top_level(gen_src).items() if not k.startswith("generate")}
    helpers = _bundle_helpers(index, names)
    if not helpers:
        return ver_src, label
    # No banner comments: the wrapper's own docstring names the task, and the
    # transform's name says what it is. The bundled helpers simply precede it.
    return helpers.rstrip() + "\n\n\n" + ver_src.strip() + "\n", label


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
        # The index puts the canonical candidate first; that one is the gold
        # oracle, so it is the only one the teacher should read.
        cid, path = files[0]
        text = _read_text(path)
        return (f"# candidate {cid} ({path.name})\n{text}" if text else None), str(path)
    if dataset == "conceptarc":
        program = getattr(session.task, "_conceptarc_program_json", None)
        if isinstance(program, dict):
            from framework.inverse_query.conceptarc_dsl_source import conceptarc_verifier_source

            bundled, _info = conceptarc_verifier_source(program.get("program") or program)
            return (bundled or json.dumps(program, indent=2)), "conceptarc DSL program"
        from framework.integrations.conceptarc_adapter import _program_path

        path = _program_path(task_id)
        if path is None:
            return None, None
        data = json.loads(path.read_text(encoding="utf-8"))
        # The descriptor alone says nothing a reader can use; bundle the
        # interpreter, trimmed to this program's branches, the way RE-ARC
        # verifiers come with the DSL primitives they call.
        from framework.inverse_query.conceptarc_dsl_source import conceptarc_verifier_source

        program = data.get("program") or {}
        bundled, _info = conceptarc_verifier_source(program)
        if bundled:
            return bundled, str(path)
        slim = {k: data[k] for k in ("concept", "program_kind", "program") if k in data}
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
    if session.dataset in ("arc", "arc2", "parc"):
        # P-ARC too: the Test2 JSONs carry no rule text, the aggregate has the
        # generator docstrings for all 50 tasks.
        from framework.integrations.nl_rules import collected_rule

        found = collected_rule(session.task_id, session.dataset)
        return found[0] if found else None
    return None


def _nl_rule_source(session: ActiveArcTrialSession) -> Optional[str]:
    if session.dataset in ("arc", "arc2", "parc"):
        from framework.integrations.nl_rules import collected_rule

        found = collected_rule(session.task_id, session.dataset)
        return found[1] if found else None
    if session.dataset == "conceptarc":
        from framework.integrations.conceptarc_adapter import conceptarc_ground_truth_rule

        return "conceptarc_rules_csv" if conceptarc_ground_truth_rule(session.task_id) else "program_description"
    return None


def _local_custom_source(task_id: str) -> tuple[Optional[str], Optional[str]]:
    """Source of the hand-written verifier in ``framework/custom_verifiers``."""
    import inspect

    try:
        from framework.custom_verifiers.registry import get_custom_verifier
        fn = get_custom_verifier(task_id)
    except Exception:
        return None, None
    if fn is None:
        return None, None
    try:
        module = inspect.getmodule(fn)
        # A fixes/<task_id>.py module is one verifier; show the whole file. An
        # in-registry _solve_<task_id> shows just that function and its helpers
        # would be noise, so the function alone.
        if module is not None and module.__name__.endswith("fixes.%s" % task_id):
            return inspect.getsource(module), "framework/custom_verifiers/fixes/%s.py" % task_id
        return inspect.getsource(fn), "framework/custom_verifiers/registry.py::%s" % fn.__name__
    except (OSError, TypeError):
        return None, None


def load_task_programs(session: ActiveArcTrialSession) -> TaskPrograms:
    """Collect what the teacher is handed: the gold verifier's source and the rule.

    No generator: the teacher gets one verified example, the natural-language
    rule and the verifier that judges the exam -- nothing that describes the
    input distribution.
    """
    slot = session.verifier_slot
    ver_src: Optional[str] = None
    ver_label: Optional[str] = None
    ver_kind: Optional[str] = None
    program_json: Optional[Dict[str, Any]] = None

    if session.dataset == "parc":
        ver_src, ver_label = _parc_verifier_source(session.task_id)
        ver_kind = "parc"
    elif session.dataset == "conceptarc":
        ver_src, ver_label = _custom_verifier_source(session)
        ver_kind = "conceptarc"
        program_json = _conceptarc_descriptor(session)
    else:
        if slot == "re_arc":
            ver_src = _re_arc_verifier_source(session.task_id)
            if ver_src:
                ver_label, ver_kind = f"re_arc verify_{session.task_id}", "re_arc"
        elif slot in ("google", "keymoon", "neurips"):
            ver_src = _golf_verifier_source(session.task_id, slot)
            path = golf_solution_path(session.task_id, slot)  # type: ignore[arg-type]
            ver_label = str(path) if path is not None else slot
            ver_kind = slot
        elif slot == "custom":
            if session.dataset == "arc":
                ver_src, ver_label = _local_custom_source(session.task_id)
            if ver_src is None:
                ver_src, ver_label = _custom_verifier_source(session)
            if ver_src:
                ver_kind = "custom"

    return TaskPrograms(
        generator_source=None,
        generator_label=None,
        verifier_source=ver_src,
        verifier_label=ver_label,
        verifier_slot=slot,
        nl_rule=_nl_rule(session),
        generator_kind=None,
        verifier_kind=ver_kind,
        nl_rule_source=_nl_rule_source(session),
        verifier_program_json=program_json,
    )


def _conceptarc_descriptor(session: ActiveArcTrialSession) -> Optional[Dict[str, Any]]:
    """The DSL program without its layout: what the verifier does, not how inputs are made."""
    program = getattr(session.task, "_conceptarc_program_json", None)
    if not isinstance(program, dict):
        from framework.integrations.conceptarc_adapter import _program_path

        path = _program_path(session.task_id)
        if path is None:
            return None
        program = json.loads(Path(path).read_text(encoding="utf-8"))
    inner = program.get("program") if isinstance(program.get("program"), dict) else program
    return {k: v for k, v in inner.items() if k != "layout"}
