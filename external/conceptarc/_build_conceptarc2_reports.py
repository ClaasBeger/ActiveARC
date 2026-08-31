#!/usr/bin/env python3
"""Compare ConceptARC-2 train/test examples against ConceptARC-GEN DSL programs."""

from __future__ import annotations

import json
import re
import signal
from collections import Counter, defaultdict
from html import escape
from pathlib import Path

from export_to_activearc import CONCEPTS, _official_program

V1_ROOT = Path("/Users/claas/Documents/SFI/ConceptARC/corpus")
V2_ROOT = Path("/Users/claas/Documents/SFI/ConceptARC-2/ConceptARC-2/corpus-2")
OUT_TRAIN = Path(
    "/Users/claas/Documents/SFI/ActiveARC/ActiveARC/external/conceptarc/"
    "conceptarc2_dsl_mismatches.html"
)
OUT_TEST = Path(
    "/Users/claas/Documents/SFI/ActiveARC/ActiveARC/external/conceptarc/"
    "conceptarc2_test_coverage.html"
)

COLORS = {
    0: "#000000",
    1: "#0074D9",
    2: "#FF4136",
    3: "#2ECC40",
    4: "#FFDC00",
    5: "#AAAAAA",
    6: "#F012BE",
    7: "#FF851B",
    8: "#7FDBFF",
    9: "#870C25",
}
FOLDER_TO_CORPUS = {
    "abovebelow": "AboveBelow",
    "center": "Center",
    "copy": "Copy",
    "count": "Count",
    "extendtoboundary": "ExtendToBoundary",
    "extractobjects": "ExtractObjects",
    "fillednotfilled": "FilledNotFilled",
    "horizontalvertical": "HorizontalVertical",
    "insideoutside": "InsideOutside",
    "movetoboundary": "MoveToBoundary",
    "order": "Order",
    "samedifferent": "SameDifferent",
    "topbottom2d": "TopBottom2D",
    "topbottom3d": "TopBottom3D",
    "cleanup": "CleanUp",
    "completeshape": "CompleteShape",
}
ANNOTATIONS = {
    ("count", 5): "Actual corpus change (e.g. external color change) — not a generator bug.",
}
MAX_TEST = 5
TRANSFORM_TIMEOUT_S = 5


class _Timeout(Exception):
    pass


def _on_alarm(signum, frame):  # noqa: ARG001
    raise _Timeout("transform timed out")


def folder_corpus(name: str) -> str | None:
    n = name[:-3] if name.endswith("_v2") else name
    return FOLDER_TO_CORPUS.get(n.lower().replace("_", ""))


def gkey(g):
    return tuple(tuple(int(c) for c in row) for row in g)


def dkey(ex):
    return (gkey(ex["input"]), gkey(ex["output"]))


def task_number(stem: str, corpus: str, prefix: str) -> int | None:
    for head in (corpus, prefix):
        if stem.lower().startswith(head.lower()):
            rest = stem[len(head) :]
            m = re.fullmatch(r"(\d+)", rest)
            if m:
                return int(m.group(1))
    m = re.search(r"(\d+)$", stem)
    return int(m.group(1)) if m else None


def run_transform(module, program, inp):
    signal.signal(signal.SIGALRM, _on_alarm)
    signal.alarm(TRANSFORM_TIMEOUT_S)
    try:
        return module.transform(program, inp), None
    except _Timeout as e:
        return None, str(e)
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
    finally:
        signal.alarm(0)


def grid_html(grid, title, highlight=None):
    if grid is None:
        return f"<div class='panel'><h3>{escape(title)}</h3><p class='err'>n/a</p></div>"
    h = len(grid)
    w = len(grid[0]) if grid else 0
    cell = max(8, min(18, int(240 / max(h, w, 1))))
    rows = []
    for r, row in enumerate(grid):
        tds = []
        for c, val in enumerate(row):
            v = int(val)
            border = (
                "outline:2px solid #fff;"
                if highlight and (r, c) in highlight
                else ""
            )
            tds.append(
                f"<td style='width:{cell}px;height:{cell}px;background:{COLORS.get(v, '#333')};{border}' "
                f"title='({r},{c})={v}'></td>"
            )
        rows.append("<tr>" + "".join(tds) + "</tr>")
    return (
        f"<div class='panel'><h3>{escape(title)}</h3>"
        f"<div class='meta'>{h}×{w}</div>"
        f"<table class='grid'>{''.join(rows)}</table></div>"
    )


def diff_cells(a, b):
    if a is None or b is None:
        return set()
    out = set()
    for r in range(max(len(a), len(b))):
        for c in range(max(len(a[0]) if a else 0, len(b[0]) if b else 0)):
            av = a[r][c] if r < len(a) and c < len(a[r]) else None
            bv = b[r][c] if r < len(b) and c < len(b[r]) else None
            if av != bv:
                out.add((r, c))
    return out


def main() -> None:
    corpus_to_concept = {cfg["corpus"]: concept for concept, cfg in CONCEPTS.items()}

    # ---- train mismatches HTML with annotations ----
    train_mismatches = []
    for d2 in sorted(V2_ROOT.iterdir()):
        if not d2.is_dir() or d2.name == "Transfer_Learning":
            continue
        corpus = folder_corpus(d2.name)
        if not corpus:
            continue
        concept = corpus_to_concept[corpus]
        cfg = CONCEPTS[concept]
        module = cfg["module"]
        prefix = cfg["prefix"]
        d1 = V1_ROOT / corpus

        for f2 in sorted(d2.glob("*.json")):
            if f2.name.endswith("_old.json"):
                continue
            number = task_number(f2.stem, corpus, prefix)
            if number is None:
                continue
            try:
                program = _official_program(cfg, number)
            except Exception:
                continue
            tr2 = json.loads(f2.read_text()).get("train", [])
            f1_matches = (
                [p for p in d1.glob("*.json") if p.name.lower() == f2.name.lower()]
                if d1.is_dir()
                else []
            )
            tr1 = (
                json.loads(f1_matches[0].read_text()).get("train", [])
                if f1_matches
                else []
            )

            for i, ex in enumerate(tr2):
                if i < len(tr1):
                    kind = "content_diff" if dkey(tr1[i]) != dkey(ex) else "unchanged"
                else:
                    kind = "extra_v2"
                if kind == "unchanged":
                    continue
                got, err = run_transform(module, program, ex["input"])
                ok = got is not None and gkey(got) == gkey(ex["output"])
                if ok:
                    continue
                if err is None:
                    err = "mismatch"
                v1_ex = tr1[i] if i < len(tr1) else None
                train_mismatches.append(
                    {
                        "concept": concept,
                        "number": number,
                        "task": f"{concept}/{prefix}{number}",
                        "file": f2.name,
                        "idx": i,
                        "kind": kind,
                        "input": ex["input"],
                        "expected": ex["output"],
                        "got": got,
                        "v1_output": v1_ex["output"] if v1_ex else None,
                        "err": err,
                        "note": ANNOTATIONS.get((concept, number)),
                    }
                )

    sections = []
    for m in train_mismatches:
        hl = diff_cells(m["expected"], m["got"]) if m["got"] is not None else set()
        err_html = f"<p class='err'>{escape(m['err'])}</p>" if m["err"] else ""
        note_html = f"<p class='note'>{escape(m['note'])}</p>" if m["note"] else ""
        tag = m["kind"]
        if m["note"]:
            tag += " · intentional change"
        v1_block = ""
        if m["kind"] == "content_diff" and m["v1_output"] is not None:
            v1_block = grid_html(
                m["v1_output"],
                "ConceptARC v1 output",
                diff_cells(m["expected"], m["v1_output"]),
            )
        sections.append(
            f"""
    <section class='case{" intentional" if m["note"] else ""}'>
      <h2>{escape(m['task'])} · train[{m['idx']}] <span class='tag'>{escape(tag)}</span></h2>
      <p class='sub'>{escape(m['file'])}</p>
      {note_html}
      {err_html}
      <div class='row'>
        {grid_html(m['input'], 'Input')}
        {grid_html(m['expected'], 'ConceptARC-2 expected', hl)}
        {grid_html(m['got'], 'DSL got', hl)}
        {v1_block}
      </div>
    </section>
    """
        )

    train_html = f"""<!DOCTYPE html>
<html><head>
<meta charset='utf-8'/>
<title>ConceptARC-2 vs DSL mismatches</title>
<style>
  body {{ font-family: ui-sans-serif, system-ui, sans-serif; margin: 24px; background: #111; color: #eee; }}
  h1 {{ font-size: 1.4rem; }}
  h2 {{ font-size: 1.1rem; margin: 0 0 4px; }}
  .sub {{ opacity: 0.7; margin: 0 0 12px; font-size: 0.9rem; }}
  .summary {{ opacity: 0.85; margin-bottom: 24px; }}
  .case {{ border: 1px solid #333; border-radius: 10px; padding: 16px; margin-bottom: 20px; background: #1a1a1a; }}
  .case.intentional {{ border-color: #3d6b3d; background: #152015; }}
  .row {{ display: flex; flex-wrap: wrap; gap: 16px; align-items: flex-start; }}
  .panel {{ background: #222; padding: 10px; border-radius: 8px; }}
  .panel h3 {{ margin: 0 0 6px; font-size: 0.85rem; font-weight: 600; }}
  .meta {{ opacity: 0.6; font-size: 0.75rem; margin-bottom: 6px; }}
  table.grid {{ border-collapse: collapse; }}
  table.grid td {{ padding: 0; border: 1px solid #111; }}
  .tag {{ display: inline-block; font-size: 0.75rem; background: #444; padding: 2px 8px; border-radius: 999px; margin-left: 8px; vertical-align: middle; }}
  .err {{ color: #ff6b6b; background: #2a1515; padding: 8px 10px; border-radius: 6px; }}
  .note {{ color: #b6e3b6; background: #1c331c; padding: 8px 10px; border-radius: 6px; }}
</style>
</head><body>
<h1>ConceptARC-2 train demos the DSL does not reproduce</h1>
<p class='summary'>{len(train_mismatches)} mismatched cases.
White outline marks cells that differ between ConceptARC-2 expected and DSL output.
Green-bordered cases are intentional corpus changes.</p>
{''.join(sections)}
</body></html>
"""
    OUT_TRAIN.write_text(train_html, encoding="utf-8")
    print(f"Updated {OUT_TRAIN} ({len(train_mismatches)} cases)", flush=True)

    # ---- first 5 test examples ----
    test_results = []
    for d2 in sorted(V2_ROOT.iterdir()):
        if not d2.is_dir() or d2.name == "Transfer_Learning":
            continue
        corpus = folder_corpus(d2.name)
        if not corpus:
            continue
        concept = corpus_to_concept[corpus]
        cfg = CONCEPTS[concept]
        module = cfg["module"]
        prefix = cfg["prefix"]
        print(f"Testing {concept}...", flush=True)

        for f2 in sorted(d2.glob("*.json")):
            if f2.name.endswith("_old.json"):
                continue
            number = task_number(f2.stem, corpus, prefix)
            if number is None:
                continue
            try:
                program = _official_program(cfg, number)
            except Exception as e:
                print(f"  skip {f2.name}: program load {e}", flush=True)
                continue
            tests = json.loads(f2.read_text()).get("test", [])[:MAX_TEST]
            for i, ex in enumerate(tests):
                got, err = run_transform(module, program, ex["input"])
                ok = got is not None and gkey(got) == gkey(ex["output"])
                if not ok and err is None:
                    err = "mismatch"
                test_results.append(
                    {
                        "concept": concept,
                        "task": f"{concept}/{prefix}{number}",
                        "idx": i,
                        "ok": ok,
                        "err": err,
                        "input": ex["input"],
                        "expected": ex["output"],
                        "got": got,
                    }
                )

    checked = test_results
    passed = sum(1 for r in checked if r["ok"])
    failed = [r for r in checked if not r["ok"]]
    by_concept: dict[str, Counter] = defaultdict(Counter)
    for r in checked:
        by_concept[r["concept"]]["ok" if r["ok"] else "fail"] += 1
        by_concept[r["concept"]]["total"] += 1

    print(
        f"\nTest coverage (first {MAX_TEST} per task): "
        f"{passed}/{len(checked)} pass, {len(failed)} fail",
        flush=True,
    )
    for c in sorted(by_concept):
        s = by_concept[c]
        print(f"  {c}: {s['ok']}/{s['total']} pass", flush=True)
    print("Failures:", flush=True)
    for r in failed:
        print(f"  {r['task']} test[{r['idx']}] {r['err']}", flush=True)

    fail_sections = []
    for m in failed:
        hl = diff_cells(m["expected"], m["got"]) if m["got"] is not None else set()
        fail_sections.append(
            f"""
    <section class='case'>
      <h2>{escape(m['task'])} · test[{m['idx']}]</h2>
      <p class='err'>{escape(m['err'] or '')}</p>
      <div class='row'>
        {grid_html(m['input'], 'Input')}
        {grid_html(m['expected'], 'ConceptARC-2 expected', hl)}
        {grid_html(m['got'], 'DSL got', hl)}
      </div>
    </section>
    """
        )

    rows = []
    for c in sorted(by_concept):
        s = by_concept[c]
        rows.append(
            f"<tr><td>{escape(c)}</td><td>{s['ok']}</td>"
            f"<td>{s['fail']}</td><td>{s['total']}</td></tr>"
        )

    report = f"""<!DOCTYPE html>
<html><head>
<meta charset='utf-8'/>
<title>ConceptARC-2 test coverage (first {MAX_TEST})</title>
<style>
  body {{ font-family: ui-sans-serif, system-ui, sans-serif; margin: 24px; background: #111; color: #eee; }}
  h1 {{ font-size: 1.4rem; }}
  table.summary {{ border-collapse: collapse; margin: 16px 0 28px; }}
  table.summary th, table.summary td {{ border: 1px solid #333; padding: 6px 10px; text-align: left; }}
  .case {{ border: 1px solid #333; border-radius: 10px; padding: 16px; margin-bottom: 20px; background: #1a1a1a; }}
  .row {{ display: flex; flex-wrap: wrap; gap: 16px; }}
  .panel {{ background: #222; padding: 10px; border-radius: 8px; }}
  .panel h3 {{ margin: 0 0 6px; font-size: 0.85rem; }}
  .meta {{ opacity: 0.6; font-size: 0.75rem; margin-bottom: 6px; }}
  table.grid {{ border-collapse: collapse; }}
  table.grid td {{ padding: 0; border: 1px solid #111; }}
  .err {{ color: #ff6b6b; background: #2a1515; padding: 8px 10px; border-radius: 6px; }}
  .ok {{ color: #b6e3b6; }}
</style>
</head><body>
<h1>ConceptARC-2 · first {MAX_TEST} test examples vs DSL</h1>
<p><span class='ok'>{passed}/{len(checked)} pass</span> · {len(failed)} fail · source: ConceptARC-2 corpus-2</p>
<table class='summary'>
<tr><th>Concept</th><th>Pass</th><th>Fail</th><th>Checked</th></tr>
{''.join(rows)}
</table>
<h2>Failures ({len(failed)})</h2>
{''.join(fail_sections) if fail_sections else '<p class="ok">None</p>'}
</body></html>
"""
    OUT_TEST.write_text(report, encoding="utf-8")
    print(f"Wrote {OUT_TEST}", flush=True)


if __name__ == "__main__":
    main()
