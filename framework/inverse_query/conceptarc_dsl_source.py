"""Readable source for a ConceptARC DSL verifier: the interpreter, trimmed to the program.

A ConceptARC "verifier" is a small JSON descriptor -- selector op, action op, a
few parameters -- interpreted by ConceptARC-GEN. The descriptor alone tells a
reader nothing about what the ops do, the same way a RE-ARC verifier would be
opaque without the DSL primitives it calls. So, like RE-ARC, the implementation
is bundled alongside: the two dispatch functions cut down to the branches this
program actually takes, plus every named helper those branches reach.

Only the verify side is included. Layout ops, the catalog and the per-concept
generators describe how inputs are produced, and the teacher is not given that.
"""

from __future__ import annotations

import ast
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from framework.inverse_query.sources import (
    _bundle_helpers,
    _index_top_level,
    _read_text,
    _referenced_names,
)

# Verify-side modules, in the order their definitions are emitted.
_HELPER_MODULES: Tuple[str, ...] = (
    "utils.py",
    "tasks/geometry.py",
    "tasks/primitives.py",
    "dsl_core.py",
    "dsl_scene.py",
    "dsl_footprints.py",
    "dsl_shape_instances.py",
    "dsl_patterns.py",
    "counting.py",
    "dsl_selectors.py",
    "dsl_actions.py",
)
_SELECTOR_DISPATCH = ("dsl_selectors.py", "select_scene_objects", "op")
_ACTION_DISPATCH = ("dsl_actions.py", "transform_dsl_program", "action_op")

# Keys under which a selector or action nests another selector / action.
_SELECTOR_CHILD_KEYS = (
    "container_selector", "candidate_selector", "reference_selector", "fallback",
    "selector", "selectors", "left", "right", "source", "target", "a", "b",
)
_ACTION_CHILD_KEYS = ("if_true", "if_false", "then", "else", "action", "actions")


def _gen_root() -> Optional[Path]:
    from framework.integrations.conceptarc_adapter import _resolve_gen_root

    root = _resolve_gen_root()
    return (root / "conceptarc_gen") if root else None


@lru_cache(maxsize=1)
def _helper_index() -> Dict[str, str]:
    """Top-level definitions of every verify-side module, first definition wins."""
    root = _gen_root()
    if root is None:
        return {}
    out: Dict[str, str] = {}
    for rel in _HELPER_MODULES:
        text = _read_text(root / rel)
        if not text:
            continue
        for name, chunk in _index_top_level(text).items():
            out.setdefault(name, chunk)
    # The dispatchers are emitted separately, trimmed to the program; a helper
    # that re-enters selection must not pull the full ones (and with them every
    # selector in the package) back in.
    out.pop(_SELECTOR_DISPATCH[1], None)
    out.pop(_ACTION_DISPATCH[1], None)
    return out


def _ops_in(node: Any, child_keys: Iterable[str]) -> Set[str]:
    """Every ``op`` string reachable through the nesting keys of a descriptor."""
    ops: Set[str] = set()
    if isinstance(node, dict):
        if isinstance(node.get("op"), str):
            ops.add(node["op"])
        for key in child_keys:
            if key in node:
                ops |= _ops_in(node[key], child_keys)
    elif isinstance(node, list):
        for item in node:
            ops |= _ops_in(item, child_keys)
    return ops


def _strings_in(node: Any) -> Set[str]:
    """Every string value in a descriptor (op names, regions, relations, colours...)."""
    out: Set[str] = set()
    if isinstance(node, dict):
        for v in node.values():
            out |= _strings_in(v)
    elif isinstance(node, list):
        for v in node:
            out |= _strings_in(v)
    elif isinstance(node, str):
        out.add(node)
    return out


@lru_cache(maxsize=1)
def _program_vocabulary() -> frozenset:
    """String values any official program can supply.

    A helper branch testing for one of these that this program does not supply
    cannot run for it and is dropped. Literals outside the vocabulary are values
    computed at run time (colours, directions...), so those branches are kept.
    """
    import re as _re
    from framework.integrations.conceptarc_adapter import list_conceptarc_task_ids, _program_path

    vocab: Set[str] = set()
    for tid in list_conceptarc_task_ids():
        m = _re.search(r"(\d+)$", tid.split("/")[-1])
        if not m or not 1 <= int(m.group(1)) <= 10:
            continue
        try:
            prog = json.loads(Path(_program_path(tid)).read_text(encoding="utf-8")).get("program") or {}
        except Exception:
            continue
        vocab |= _strings_in({k: v for k, v in prog.items() if k != "layout"})
    return frozenset(vocab)


class _PruneUnusedBranches(ast.NodeTransformer):
    """Drop ``if x == "lit"`` / ``if x in {...}`` branches on program strings this program lacks."""

    def __init__(self, used: Set[str], vocab: frozenset):
        self.used, self.vocab = used, vocab

    def _literals(self, test: ast.expr) -> Optional[List[str]]:
        if not isinstance(test, ast.Compare) or len(test.comparators) != 1:
            return None
        comp, op = test.comparators[0], test.ops[0]
        if isinstance(op, ast.Eq) and isinstance(comp, ast.Constant) and isinstance(comp.value, str):
            return [comp.value]
        if isinstance(op, ast.In) and isinstance(comp, (ast.Set, ast.Tuple, ast.List)):
            vals = [e.value for e in comp.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
            return vals if len(vals) == len(comp.elts) and vals else None
        return None

    def visit_If(self, node: ast.If):
        lits = self._literals(node.test)
        if lits and all(l in self.vocab for l in lits) and not any(l in self.used for l in lits):
            # the whole branch is unreachable for this program; keep only its else
            if node.orelse:
                return [self.visit(n) for n in node.orelse]
            return None
        return self.generic_visit(node)


def _prune_helper(source: str, used: Set[str], vocab: frozenset) -> str:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source
    tree = _PruneUnusedBranches(used, vocab).visit(tree)
    ast.fix_missing_locations(tree)
    try:
        return ast.unparse(tree)
    except Exception:
        return source


def _branch_matches(test: ast.expr, var: str, ops: Set[str]) -> bool:
    """Whether ``if <var> == "x"`` / ``if <var> in {...}`` selects one of *ops*."""
    if not isinstance(test, ast.Compare) or len(test.comparators) != 1:
        return False
    left = test.left
    if not (isinstance(left, ast.Name) and left.id == var):
        return False
    comp = test.comparators[0]
    op = test.ops[0]
    if isinstance(op, ast.Eq) and isinstance(comp, ast.Constant):
        return comp.value in ops
    if isinstance(op, ast.In) and isinstance(comp, (ast.Set, ast.Tuple, ast.List)):
        return any(isinstance(e, ast.Constant) and e.value in ops for e in comp.elts)
    return False


def _trim_dispatcher(source: str, func_name: str, var: str, ops: Set[str]) -> Tuple[Optional[str], Set[str]]:
    """The dispatcher with only the branches for *ops*; also which ops were found.

    Statements before the first ``if <var> ...`` (the prelude that computes the
    selection, reads the op, etc.) are kept; every branch that does not test for
    one of *ops* is dropped.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None, set()
    fn = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == func_name), None)
    if fn is None:
        return None, set()
    kept: List[str] = []
    found: Set[str] = set()
    seen_branch = False

    def _seg(stmt: ast.stmt) -> str:
        # get_source_segment drops the first line's indentation; put it back so
        # the trimmed function is still valid Python.
        return " " * stmt.col_offset + (ast.get_source_segment(source, stmt) or "")

    for stmt in fn.body:
        is_branch = isinstance(stmt, ast.If) and isinstance(stmt.test, ast.Compare) \
            and isinstance(stmt.test.left, ast.Name) and stmt.test.left.id == var
        if not is_branch:
            if not seen_branch:
                kept.append(_seg(stmt))
            continue
        seen_branch = True
        if _branch_matches(stmt.test, var, ops):
            kept.append(_seg(stmt))
            comp = stmt.test.comparators[0]
            consts = [comp] if isinstance(comp, ast.Constant) else list(getattr(comp, "elts", []))
            found |= {c.value for c in consts if isinstance(c, ast.Constant) and c.value in ops}
    header_end = fn.body[0].lineno - 1
    header = "\n".join(source.splitlines()[fn.lineno - 1:header_end]).rstrip()
    indent = " " * (fn.body[0].col_offset if fn.body else 4)
    body = "\n".join(kept) if kept else indent + "pass"
    note = indent + "# Dispatch trimmed to the branch(es) this program uses.\n"
    trimmed = header + "\n" + note + body
    try:
        ast.parse(trimmed)
    except SyntaxError:
        return None, set()
    return trimmed, found


def _indent_of(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line[: len(line) - len(line.lstrip())]
    return "    "


def conceptarc_verifier_source(program: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
    """Bundled, trimmed interpreter source for *program*, plus a small report.

    Returns ``(source, info)``; *source* is ``None`` if ConceptARC-GEN is not
    available. *info* lists the ops that had no dispatch branch, so a caller can
    tell an incomplete bundle from a complete one.
    """
    root = _gen_root()
    if root is None:
        return None, {"error": "ConceptARC-GEN not found"}
    selector_ops = _ops_in(program.get("selector"), _SELECTOR_CHILD_KEYS)
    action_ops = _ops_in(program.get("action"), _ACTION_CHILD_KEYS)

    sel_src = _read_text(root / _SELECTOR_DISPATCH[0]) or ""
    act_src = _read_text(root / _ACTION_DISPATCH[0]) or ""
    sel_trim, sel_found = _trim_dispatcher(sel_src, _SELECTOR_DISPATCH[1], _SELECTOR_DISPATCH[2], selector_ops)
    act_trim, act_found = _trim_dispatcher(act_src, _ACTION_DISPATCH[1], _ACTION_DISPATCH[2], action_ops)

    used = _strings_in({k: v for k, v in program.items() if k != "layout"})
    vocab = _program_vocabulary()
    # Helpers are pruned *before* the closure walk, so a dropped branch cannot
    # seed further helpers.
    index = {name: _prune_helper(src, used, vocab) for name, src in _helper_index().items()}
    seeds: Set[str] = set()
    for chunk in (sel_trim, act_trim):
        if chunk:
            seeds |= _referenced_names(chunk)
    seeds -= {_SELECTOR_DISPATCH[1], _ACTION_DISPATCH[1]}
    helpers = _bundle_helpers(index, seeds)

    shown = {k: v for k, v in program.items() if k != "layout"}
    parts: List[str] = [
        "# ConceptARC DSL program (the verifier is this descriptor, run by the interpreter below):",
        "# " + json.dumps(shown, separators=(",", ": ")),
        "# Entry point: output = transform_dsl_program(program, input_grid)",
        "",
        "# --- action: how the selection is turned into the output grid ---", "",
        act_trim or "# (action dispatch not found)", "",
        "# --- selection: which cells/objects the program operates on ---", "",
        sel_trim or "# (selector dispatch not found)", "",
    ]
    if helpers:
        parts += ["# --- helpers the branches above reach (ConceptARC-GEN, verify side only; "
                  "`common.grid(w, h, c)` is ARC-GEN's blank-grid constructor) ---", "",
                  helpers, ""]
    info = {
        "selector_ops": sorted(selector_ops), "action_ops": sorted(action_ops),
        "unmatched_selector_ops": sorted(selector_ops - sel_found),
        "unmatched_action_ops": sorted(action_ops - act_found),
        "n_helpers": len(helpers.split("\n\n")) if helpers else 0,
    }
    return "\n".join(parts), info
