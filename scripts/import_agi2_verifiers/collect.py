"""Collect and normalize candidate verifiers for the 500 ARC-GEN V2 tasks."""

from __future__ import annotations

import ast
import json
import logging
import re
import textwrap
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .ct_pang_align import align_ct_pang, load_ct_pang_primitives
from .paths import (
    ARC_GEN_V2,
    ARUN,
    CANDIDATES,
    GITMONSTERS,
    LOGS,
    OUT,
)

logger = logging.getLogger(__name__)

LICENSE_GITMONSTERS = (
    "NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; "
    "retain upstream attribution and review before redistribution."
)
LICENSE_ARUN_MIT = "MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)"
LICENSE_ARUN_BARC = (
    "NOASSERTION — converted BARC seeds (xu3kev/BARC); BARC publishes no LICENSE; "
    "see arc-agi2-solutions/NOTICE"
)
LICENSE_CTPANG = (
    "NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; "
    "retain upstream attribution and review before redistribution."
)


@dataclass
class CandidateMeta:
    candidate_id: str
    task_id: str
    source: str
    original_path: str
    license: str
    entrypoint: str  # e.g. solve / transform / solve_<id>
    relative_path: str  # under candidates/


def v2_task_ids() -> List[str]:
    return sorted(p.stem.replace("task_", "") for p in ARC_GEN_V2.glob("task_*.py"))


def _write_verify_module(
    dest: Path,
    *,
    body: str,
    call_expr: str,
    meta: CandidateMeta,
    extra_imports: str = "",
) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    header = textwrap.dedent(
        f'''\
        """Auto-normalized ARC-AGI-2 verifier candidate.

        task_id: {meta.task_id}
        source: {meta.source}
        original_path: {meta.original_path}
        license: {meta.license}
        candidate_id: {meta.candidate_id}
        """
        from __future__ import annotations

        {extra_imports}

        '''
    )
    # Indent body to module level (already module-level source)
    verify_fn = textwrap.dedent(
        f'''\

        def verify(input_grid):
            """Normalized verifier entrypoint."""
            _result = {call_expr}
            return _result
        '''
    )
    dest.write_text(header + body.rstrip() + "\n" + verify_fn)
    meta.relative_path = str(dest.relative_to(CANDIDATES))
    (dest.with_suffix(dest.suffix + ".meta.json")).write_text(
        json.dumps(asdict(meta), indent=2)
    )


def _strip_main_block(source: str) -> str:
    """Remove ``if __name__ == '__main__':`` blocks for safer import."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source
    lines = source.splitlines(keepends=True)
    cut_spans = []
    for node in tree.body:
        if isinstance(node, ast.If):
            test = node.test
            if (
                isinstance(test, ast.Compare)
                and isinstance(test.left, ast.Name)
                and test.left.id == "__name__"
            ):
                cut_spans.append((node.lineno - 1, node.end_lineno or node.lineno))
    if not cut_spans:
        return source
    keep = []
    skip = set()
    for a, b in cut_spans:
        for i in range(a, b):
            skip.add(i)
    for i, line in enumerate(lines):
        if i not in skip:
            keep.append(line)
    return "".join(keep)


def collect_gitmonsters(v2: set) -> List[CandidateMeta]:
    metas: List[CandidateMeta] = []
    catalog = json.loads((GITMONSTERS / "catalog.json").read_text())
    by_id = {e["id"]: e for e in catalog if isinstance(e, dict) and "id" in e}
    for tid in sorted(v2):
        solver = GITMONSTERS / "solves" / tid / "solver.py"
        if not solver.is_file():
            continue
        entry = by_id.get(tid, {})
        if entry and entry.get("status") not in (None, "verified_solved"):
            # Still import as candidate; catalog marks unverified separately
            pass
        src = _strip_main_block(solver.read_text(encoding="utf-8", errors="replace"))
        cid = f"gitmonsters__{tid}"
        meta = CandidateMeta(
            candidate_id=cid,
            task_id=tid,
            source="GitMonsters/SOLVED-562-verified",
            original_path=str(solver.relative_to(GITMONSTERS)),
            license=LICENSE_GITMONSTERS,
            entrypoint="solve",
            relative_path="",
        )
        dest = CANDIDATES / tid / f"{cid}.py"
        _write_verify_module(dest, body=src, call_expr="solve(input_grid)", meta=meta)
        metas.append(meta)
    logger.info("GitMonsters candidates: %d", len(metas))
    return metas


def _extract_solve_functions(path: Path) -> Dict[str, str]:
    """Map task_id -> full function source for each ``solve_<id>``."""
    text = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(text)
    lines = text.splitlines(keepends=True)
    out: Dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("solve_"):
            m = re.fullmatch(r"solve_([0-9a-f]{8})", node.name)
            if not m:
                continue
            start = node.lineno - 1
            end = node.end_lineno or node.lineno
            out[m.group(1)] = "".join(lines[start:end])
        elif isinstance(node, ast.Assign):
            # barc wraps: solve_xxx = _barc_xy(solve_xxx)
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.startswith("solve_"):
                    m = re.fullmatch(r"solve_([0-9a-f]{8})", t.id)
                    if m and m.group(1) in out:
                        # include wrapper assignment after function
                        start = node.lineno - 1
                        end = node.end_lineno or node.lineno
                        out[m.group(1)] = out[m.group(1)] + "\n" + "".join(lines[start:end])
    return out


def collect_arun(v2: set) -> List[CandidateMeta]:
    metas: List[CandidateMeta] = []
    specs = [
        ("our_task_solutions.py", "ArunSehrawat/arc-agi2-solutions:our", LICENSE_ARUN_MIT, False),
        ("llm_task_solutions.py", "ArunSehrawat/arc-agi2-solutions:llm", LICENSE_ARUN_MIT, False),
        ("barc_task_solutions.py", "ArunSehrawat/arc-agi2-solutions:barc", LICENSE_ARUN_BARC, True),
    ]
    for filename, source, license_text, needs_barc in specs:
        path = ARUN / filename
        funcs = _extract_solve_functions(path)
        for tid, fn_src in sorted(funcs.items()):
            if tid not in v2:
                continue
            cid = f"arun__{filename.replace('.py','')}__{tid}"
            meta = CandidateMeta(
                candidate_id=cid,
                task_id=tid,
                source=source,
                original_path=filename,
                license=license_text,
                entrypoint=f"solve_{tid}",
                relative_path="",
            )
            extras = ["import numpy as np", ""]
            body_parts = []
            if needs_barc:
                # Inline minimal import of barc_common by path injection at runtime —
                # ship a small prelude that loads barc_common from the source repo.
                extras.append(
                    "import importlib.util as _ilu\n"
                    f"_barc_path = {str(ARUN / 'barc_common.py')!r}\n"
                    "_spec = _ilu.spec_from_file_location('barc_common', _barc_path)\n"
                    "_barc = _ilu.module_from_spec(_spec)\n"
                    "_spec.loader.exec_module(_barc)\n"
                    "globals().update({k: getattr(_barc, k) for k in dir(_barc) if not k.startswith('_')})\n"
                )
            body = "\n".join(extras) + "\n" + fn_src
            dest = CANDIDATES / tid / f"{cid}.py"
            _write_verify_module(
                dest,
                body=body,
                call_expr=f"solve_{tid}(input_grid)",
                meta=meta,
                extra_imports="",
            )
            metas.append(meta)
    logger.info("ArunSehrawat candidates (V2 only): %d", len(metas))
    return metas


def collect_ct_pang(v2: set) -> Tuple[List[CandidateMeta], dict]:
    mappings, decisions = align_ct_pang()
    primitives = load_ct_pang_primitives()
    metas: List[CandidateMeta] = []
    for prog_idx, tid in sorted(mappings.items()):
        if tid not in v2:
            continue
        prim = primitives[prog_idx]
        cid = f"ctpang__prog{prog_idx:04d}__{tid}"
        meta = CandidateMeta(
            candidate_id=cid,
            task_id=tid,
            source="epang080516/arc_agi:saved_library_1000.pkl",
            original_path=f"saved_library_1000.pkl#primitives[{prog_idx}](id={prim.id})",
            license=LICENSE_CTPANG,
            entrypoint="transform",
            relative_path="",
        )
        body = (
            "import numpy as np\n\n"
            + prim.python_code_str.strip()
            + "\n"
        )
        dest = CANDIDATES / tid / f"{cid}.py"
        _write_verify_module(
            dest, body=body, call_expr="transform(input_grid)", meta=meta
        )
        metas.append(meta)
    summary = {
        "mapped_total": len(mappings),
        "mapped_v2": len(metas),
        "rejected": [
            asdict(d)
            for d in decisions
            if d.status.startswith("rejected")
        ],
    }
    (LOGS / "ct_pang_v2_import_summary.json").write_text(json.dumps(summary, indent=2))
    logger.info("CT Pang V2 candidates: %d (mapped total %d)", len(metas), len(mappings))
    return metas, summary


def collect_all() -> List[CandidateMeta]:
    CANDIDATES.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    v2 = set(v2_task_ids())
    assert len(v2) == 500, len(v2)
    metas: List[CandidateMeta] = []
    metas.extend(collect_gitmonsters(v2))
    metas.extend(collect_arun(v2))
    ct_metas, _ = collect_ct_pang(v2)
    metas.extend(ct_metas)
    index = [asdict(m) for m in metas]
    (OUT / "candidates_index.json").write_text(json.dumps(index, indent=2))
    logger.info("Total candidates written: %d", len(metas))
    return metas
