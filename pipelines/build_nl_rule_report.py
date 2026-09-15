#!/usr/bin/env python3
"""Aggregate the natural-language rules a teacher can hand a student, and show the gaps.

Four datasets, four different provenances::

    python -m pipelines.build_nl_rule_report

* ARC-AGI-1  LARC description an independent builder reconstructed the output from
* ARC-AGI-2  MARC2 description that passed description-only solver validation
* P-ARC      the rule stated in the generator module's own docstring
* ConceptARC the program's ``description`` field -- a real rule for the generated
             tasks, only a label ("Official ConceptARC AboveBelow1.") for the 160
             hand-authored ones, which is the dataset's real gap

Writes ``experiments/nl_rule_annotations.html``.
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

NL_DIR = ROOT_DIR / "external" / "nl_rules"
OUT = ROOT_DIR / "experiments" / "nl_rule_annotations.html"


# A P-ARC generator docstring states the rule and then, in 23 of 50 modules,
# goes on to describe how inputs are sampled ("Generation constraints used to
# keep examples well-formed", "Generator constraints / ambiguity controls",
# "Design:", ...). The rule is what a teacher may see; the sampling notes are
# not, so the text is cut at the first such heading.
_GENERATION_SECTION = re.compile(
    r"^\s*(Design|Generation( constraints?| goals?)?|Generator constraints?|Sampling|Diversity"
    r"|[\w-]+ constraints (enforced|used|applied)\b)[^\n]*$",
    re.M,
)
# Sentences about the sampler or its implementation inside the rule body.
# Applied per sentence, not per line: docstrings wrap mid-sentence, and a
# sentence that merely *describes the input* in generator terms ("Generated
# inputs contain ...") is kept, reworded, rather than lost.
_GENERATOR_SENTENCE = re.compile(
    r"(\bgenerate\(\)|\bgenerat(or|ed|es|ion)\b|\bsampler\b|prohibitively slow|never scans"
    r"|\brejects? (layouts|inputs|candidates)|\bskipped valid\b|\banchoring lex-first\b)",
    re.I,
)
_INPUT_REWRITES = (
    # a sentence in the generator's voice describing what it makes
    (re.compile(r"^(Creates|Builds|Draws|Places|Produces|Lays out|Constructs|Renders) (an? |the )?"), "The input shows "),
    (re.compile(r"\bGenerated inputs contain\b"), "The input contains"),
    (re.compile(r"\bGenerated inputs\b"), "Inputs"),
    (re.compile(r"\bThe generator (places|puts|draws)\b"), "The input has"),
    (re.compile(r"\bThe generator (ensures|guarantees) that\b"), "It always holds that"),
)
# The module title: "Generator for Test2/t11: diagonal rays with wall bounces."
# The tail after the colon is a fair heading; the "Generator for" framing is not.
_TITLE_PREFIX = re.compile(
    r"^\s*(Diverse )?[Gg]enerator for (Test2/)?t\d+(_\w+)?\s*[:.(]?\s*", re.M)


_TIDY = (
    (re.compile(r"\*\*(.+?)\*\*"), r"\1"),            # **bold** -> bold
    (re.compile(r"``(.+?)``"), r"\1"),                  # ``code`` -> code
    (re.compile(r"`(.+?)`"), r"\1"),
    (re.compile(r"^\s*Rule implemented:\s*$", re.M), "Rule:"),
    (re.compile(r"^\s*Inference\.\s*", re.M), ""),
)


def _tidy_rule_text(text: str) -> str:
    """Docstring markup that is noise in a rule handed to a reader."""
    for pat, rep in _TIDY:
        text = pat.sub(rep, text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _drop_generator_sentences(text: str) -> str:
    """Rewrite input descriptions, then drop sentences that are about the sampler."""
    out_paras = []
    for para in re.split(r"\n\s*\n", text):
        # bullets keep their line structure; prose is re-flowed into sentences
        if re.search(r"^\s*([-*]|\d+\))\s", para, re.M):
            lines = []
            for line in para.splitlines():
                for pat, rep in _INPUT_REWRITES:
                    line = pat.sub(rep, line)
                if not _GENERATOR_SENTENCE.search(line):
                    lines.append(line)
            if lines:
                out_paras.append("\n".join(lines))
            continue
        flat = " ".join(l.strip() for l in para.splitlines() if l.strip())
        for pat, rep in _INPUT_REWRITES:
            flat = pat.sub(rep, flat)
        sentences = re.split(r"(?<=[.!?])\s+", flat)
        kept = [x for x in sentences if x and not _GENERATOR_SENTENCE.search(x)]
        if kept:
            out_paras.append(" ".join(kept))
    return "\n\n".join(out_paras).strip()


def _docstring(path: Optional[Path]) -> Optional[str]:
    if not path or not Path(path).is_file():
        return None
    m = re.match(r'\s*"""(.*?)"""', Path(path).read_text(encoding="utf-8"), re.S)
    if not m:
        return None
    text = m.group(1).strip()
    cut = _GENERATION_SECTION.search(text)
    if cut:
        text = text[:cut.start()].rstrip()
    first, _, rest = text.partition("\n")
    stripped = _TITLE_PREFIX.sub("", first, count=1).strip().rstrip(").")
    if stripped:
        stripped = stripped[0].upper() + stripped[1:]
        if not stripped.endswith("."):
            stripped += "."
    body = _drop_generator_sentences(rest) if rest.strip() else ""
    if not body:
        return None          # a title with nothing under it is not a rule
    body = _tidy_rule_text(body)
    return (stripped + "\n\n" + body) if stripped else body


def collect() -> Dict[str, Dict[str, object]]:
    from framework.integrations.nl_rules import larc_rule, marc2_rule
    from framework.tasks.arc_dataset import list_arc_agi_1_task_ids
    from framework.integrations.agi2_verifiers import _index
    from framework.tasks.parc_dataset import list_parc_task_ids, parc_source_paths
    from framework.integrations.conceptarc_adapter import (
        conceptarc_ground_truth_rule,
        list_conceptarc_task_ids,
        _program_path,
    )

    out: Dict[str, Dict[str, object]] = {}
    out["ARC-AGI-1"] = {
        "source": "LARC — description a separate human rebuilt the test output from",
        "rules": {t: larc_rule(t) for t in list_arc_agi_1_task_ids()},
    }
    out["ARC-AGI-2"] = {
        "source": "MARC2 — description that passed description-only solver validation",
        "rules": {t: marc2_rule(t) for t in sorted(_index().keys())},
    }
    parc = {}
    for t in sorted(list_parc_task_ids()):
        gen, _ver = parc_source_paths(t)
        # None when the docstring is only the module title -- a name, not a rule.
        parc[t] = _docstring(gen)
    out["P-ARC"] = {"source": "the generator module's own docstring", "rules": parc}
    concept = {}
    concept_csv = set()
    for t in sorted(list_conceptarc_task_ids()):
        # The 160 hand-authored tasks have a human rule in the pinned copy of
        # ConceptARC-Rules/Evaluation/ConceptARC_rules.csv; the generated
        # families only have the program's own description.
        gt = conceptarc_ground_truth_rule(t)
        if gt:
            concept[t] = gt
            concept_csv.add(t)
            continue
        d = json.loads(Path(_program_path(t)).read_text(encoding="utf-8"))
        text = str(d.get("description") or "")
        # A label is not a rule; count it as missing so the gap is visible.
        concept[t] = None if text.startswith("Official ConceptARC") else text
    out["ConceptARC"] = {
        "source": "ConceptARC_rules.csv for the 160 official tasks; the DSL program's "
                  "description field for generated ones",
        "rules": concept,
        "csv_ids": concept_csv,
    }
    return out


def assignments() -> Dict[str, Dict[str, List[str]]]:
    """Who is writing which missing rule."""
    who: Dict[str, Dict[str, List[str]]] = {}
    for path in sorted(NL_DIR.glob("missing_verified_rules_*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        name = str((payload.get("_meta") or {}).get("assignee") or path.stem)
        who[name] = {
            "ARC-AGI-1": list(payload.get("arc_agi_1") or []),
            "ARC-AGI-2": list(payload.get("arc_agi_2") or []),
        }
    return who



DRAFTS_DIR = ROOT_DIR.parent / "annotations"
_TASK_ID = re.compile(r"^[0-9a-f]{8}$")


def _docx_lines(path: Path) -> List[str]:
    """The non-empty paragraphs of a .docx, without needing python-docx."""
    import zipfile

    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    out: List[str] = []
    for para in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S):
        text = html.unescape("".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", para, re.S))).strip()
        if text:
            out.append(text)
    return out


def _xlsx_rows(path: Path) -> List[List[str]]:
    """Rows of the first sheet, shared strings resolved. No openpyxl needed."""
    import zipfile

    with zipfile.ZipFile(path) as z:
        shared = [
            html.unescape(re.sub(r"<[^>]+>", "", si))
            for si in re.findall(r"<si>(.*?)</si>",
                                 z.read("xl/sharedStrings.xml").decode("utf-8"), re.S)
        ]
        sheet = z.read("xl/worksheets/sheet1.xml").decode("utf-8")
    rows: List[List[str]] = []
    for row in re.findall(r"<row[^>]*>(.*?)</row>", sheet, re.S):
        values: List[str] = []
        for cell in re.findall(r"<c\b[^>]*>.*?</c>|<c\b[^>]*/>", row, re.S):
            kind = re.search(r'\st="([^"]+)"', cell)
            value = re.search(r"<v>(.*?)</v>", cell, re.S)
            if not value:
                values.append("")
                continue
            values.append(shared[int(value.group(1))]
                          if kind and kind.group(1) == "s" else value.group(1))
        if any(values):
            rows.append(values)
    return rows


def drafts(folder: Path = DRAFTS_DIR) -> Dict[str, Tuple[str, str]]:
    """Draft rules collected by hand: ``task_id -> (rule, author)``.

    Word files are written one task per block -- the id on its own line, a LARC
    link, then the prose. The spreadsheet is a Task/Rule table. Neither carries
    an author field reliably, so the name comes from the header line, the file
    name, or failing both, whichever assignment list owns the ids.
    """
    if not folder.is_dir():
        return {}
    owner_of: Dict[str, str] = {}
    for path in sorted(NL_DIR.glob("missing_verified_rules_*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        name = str((payload.get("_meta") or {}).get("assignee") or path.stem)
        for key in ("arc_agi_1", "arc_agi_2"):
            for tid in payload.get(key) or []:
                owner_of[tid] = name

    out: Dict[str, Tuple[str, str]] = {}

    def attribute(ids: List[str], fallback: str) -> str:
        owners = [owner_of[t] for t in ids if t in owner_of]
        return max(set(owners), key=owners.count) if owners else fallback

    for path in sorted(folder.glob("*.docx")):
        if path.name.startswith("~$"):
            continue
        lines = _docx_lines(path)
        blocks: Dict[str, List[str]] = {}
        current: Optional[str] = None
        for line in lines:
            if _TASK_ID.match(line):
                current = line
                blocks.setdefault(current, [])
                continue
            if current is None or line.startswith("http"):
                continue
            blocks[current].append(line)
        author = attribute(list(blocks), re.split(r"[_\s]", path.stem)[0])
        for tid, body in blocks.items():
            text = "\n".join(body).strip()
            if text:
                out[tid] = (text, author)

    # Rules dictated in chat land here as JSON, keyed the same way. Written last
    # so a typed correction wins over an older Word draft of the same task.
    for path in sorted(NL_DIR.glob("drafts_*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        meta = payload.get("_meta") or {}
        author = str(meta.get("author") or path.stem.split("_", 1)[-1])
        for tid, text in (payload.get("rules") or {}).items():
            if str(text).strip():
                out[tid] = (str(text).strip(), author)

    for path in sorted(folder.glob("*.xlsx")):
        if path.name.startswith("~$"):
            continue
        rows = _xlsx_rows(path)
        pairs = [(r[0].strip(), r[1].strip()) for r in rows
                 if len(r) >= 2 and _TASK_ID.match(r[0].strip()) and r[1].strip()]
        author = attribute([t for t, _ in pairs], path.stem)
        for tid, text in pairs:
            out[tid] = (text, author)
    return out


CSS = """
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:0;padding:26px 30px;
background:#faf9f7;color:#1d1c1a;line-height:1.55}
h1{font-size:21px;margin:0 0 6px} h3{font-size:15px;margin:26px 0 8px;color:#43403b}
.sub{color:#6b6862;font-size:13px;max-width:92ch;margin-bottom:16px}
table{border-collapse:collapse;font-size:13px;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.06);
margin-bottom:14px;width:100%;max-width:1100px}
th,td{border-bottom:1px solid #eceae6;padding:7px 11px;text-align:left;vertical-align:top}
th{background:#f3f1ed;font-weight:600}
td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
code{background:#f0eee9;padding:1px 5px;border-radius:3px;font-size:12px}
.rule{color:#33312e;max-width:78ch;white-space:pre-wrap}
.miss{color:#8f2020;font-weight:600}
.who{background:#e8f0fb;color:#1d4e89;border-radius:10px;padding:1px 8px;font-size:12px}
.bar{height:9px;background:#eceae6;border-radius:5px;overflow:hidden;max-width:360px;margin:2px 0 8px}
.bar span{display:block;height:100%;background:#6b9c6b}
details summary{cursor:pointer;color:#5a5752}
"""


def main() -> None:
    data = collect()
    who = assignments()
    draft = drafts()
    # A hand-written draft fills a gap the published lookups leave. Keep the two
    # apart: one is independently validated, the other is a colleague's first pass.
    for ds, payload in data.items():
        rules = payload["rules"]  # type: ignore[index]
        for tid in list(rules):
            if not rules[tid] and tid in draft:
                rules[tid] = draft[tid][0]
                payload.setdefault("draft_ids", set()).add(tid)  # type: ignore[union-attr]
    owner: Dict[Tuple[str, str], str] = {}
    for name, sets in who.items():
        for ds, ids in sets.items():
            for t in ids:
                owner[(ds, t)] = name

    p = ["<meta charset=\"utf-8\"><style>%s</style>" % CSS,
         "<h1>Natural-language rules for the teacher</h1>",
         "<div class='sub'>What a teacher could state in words for each task, and where it comes from. "
         "The four datasets have four different provenances, and only two of them are independently "
         "validated &mdash; worth knowing before these are used as ground truth.</div>"]

    p.append("<table><tr><th>dataset</th><th>source</th><th class='n'>with a rule</th>"
             "<th class='n'>missing</th><th>coverage</th></tr>")
    for ds, payload in data.items():
        rules = payload["rules"]  # type: ignore[index]
        have = sum(1 for v in rules.values() if v)
        total = len(rules)
        drafted = len(payload.get("draft_ids") or ())
        p.append("<tr><td><b>%s</b></td><td>%s</td><td class='n'>%d%s</td><td class='n'>%d</td>"
                 "<td><div class='bar'><span style='width:%.0f%%'></span></div>%.0f%%</td></tr>" % (
                     ds, html.escape(str(payload["source"])), have,
                     (" <span class='who'>+%d draft</span>" % drafted) if drafted else "",
                     total - have, 100.0 * have / total, 100.0 * have / total))
    p.append("</table>")

    if who:
        p.append("<h3>Missing rules, by who is writing them</h3><table>"
                 "<tr><th>annotator</th><th>ARC-AGI-1</th><th>ARC-AGI-2</th><th class='n'>total</th></tr>")
        for name in sorted(who):
            a1 = who[name]["ARC-AGI-1"]; a2 = who[name]["ARC-AGI-2"]
            p.append("<tr><td><span class='who'>%s</span></td><td>%s</td><td>%s</td>"
                     "<td class='n'>%d</td></tr>" % (
                         html.escape(name),
                         ' '.join('<code>%s</code>' % t for t in a1),
                         ' '.join('<code>%s</code>' % t for t in a2),
                         len(a1) + len(a2)))
        p.append("</table>")

    rework_path = NL_DIR / "needs_rework.json"
    if rework_path.is_file():
        rework = json.loads(rework_path.read_text(encoding="utf-8"))
        p.append("<h3>On file, but not usable as ground truth yet</h3>"
                 "<div class='sub'>Queued for later &mdash; none of these were rewritten. "
                 "See <code>external/nl_rules/needs_rework.json</code>.</div><table>"
                 "<tr><th>issue</th><th class='n'>n</th><th>tasks</th></tr>")
        for group, body in rework.items():
            if group.startswith("_"):
                continue
            ids = list(body.get("tasks") or {})
            p.append("<tr><td>%s</td><td class='n'>%d</td><td>%s</td></tr>" % (
                html.escape(str(body.get("issue", group))), len(ids),
                ' '.join('<code>%s</code>' % t for t in ids)))
        p.append("</table>")

    for ds, payload in data.items():
        rules = payload["rules"]  # type: ignore[index]
        missing = [t for t, v in rules.items() if not v]
        have = [(t, v) for t, v in rules.items() if v]
        p.append("<h3>%s &mdash; %d with a rule (%d of them drafts), %d still missing</h3>" % (
            ds, len(have), len(payload.get("draft_ids") or ()), len(missing)))
        if missing:
            p.append("<table><tr><th>missing</th><th>assigned to</th></tr>")
            for t in missing[:200]:
                p.append("<tr><td><code>%s</code></td><td>%s</td></tr>" % (
                    t, ("<span class='who'>%s</span>" % owner[(ds, t)]) if (ds, t) in owner
                    else "<span class='miss'>unassigned</span>"))
            p.append("</table>")
        drafted = payload.get("draft_ids") or set()
        if drafted:
            p.append("<table><tr><th>task</th><th>draft rule</th><th>by</th></tr>")
            for t, v in have:
                if t not in drafted:
                    continue
                p.append("<tr><td><code>%s</code></td><td class='rule'>%s</td>"
                         "<td><span class='who'>%s</span></td></tr>" % (
                             t, html.escape(str(v)), html.escape(draft[t][1])))
            p.append("</table>")
        p.append("<details><summary>%d rules on file (published lookups)</summary><table>"
                 "<tr><th>task</th><th>rule</th></tr>" % (len(have) - len(drafted)))
        for t, v in have:
            if t in drafted:
                continue
            p.append("<tr><td><code>%s</code></td><td class='rule'>%s</td></tr>" % (
                t, html.escape(str(v))))
        p.append("</table></details>")

    OUT.write_text(''.join(p), encoding="utf-8")
    print("wrote %s (%.0f KB)" % (OUT, OUT.stat().st_size / 1024))

    # The aggregate itself, so the teacher reads one file instead of four sources
    # scattered across two repos and a folder of Word documents. Provenance is
    # kept per rule: a validated lookup and a colleague's draft are not the same
    # evidence, and a consumer may want only the former.
    key = {"ARC-AGI-1": "arc_agi_1", "ARC-AGI-2": "arc_agi_2",
           "P-ARC": "parc", "ConceptARC": "conceptarc"}
    origin = {"ARC-AGI-1": "larc", "ARC-AGI-2": "marc2",
              "P-ARC": "generator_docstring", "ConceptARC": "program_description"}
    aggregate: Dict[str, object] = {
        "_meta": {
            "built_by": "python -m pipelines.build_nl_rule_report",
            "sources": {k: str(v["source"]) for k, v in data.items()},
            "drafts_dir": str(DRAFTS_DIR),
            "validated": "true for larc, marc2 (independent human or solver "
                         "reconstruction) and conceptarc_rules_csv (the dataset "
                         "authors' rule); false for drafts, generator docstrings "
                         "and program descriptions",
        }
    }
    counts = {}
    for ds, payload in data.items():
        rules = payload["rules"]  # type: ignore[index]
        drafted = payload.get("draft_ids") or set()
        block = {}
        for tid, text in rules.items():
            if not text:
                continue
            is_draft = tid in drafted
            from_csv = tid in (payload.get("csv_ids") or ())
            entry = {
                "rule": text,
                "source": "draft" if is_draft else ("conceptarc_rules_csv" if from_csv else origin[ds]),
                # The ConceptARC CSV is the dataset authors' own statement of each
                # task's rule, so it counts as ground truth alongside LARC/MARC2.
                "validated": (not is_draft) and (ds in ("ARC-AGI-1", "ARC-AGI-2") or from_csv),
            }
            if is_draft:
                entry["author"] = draft[tid][1]
            block[tid] = entry
        aggregate[key[ds]] = block
        counts[key[ds]] = len(block)
    agg_path = NL_DIR / "collected_rules.json"
    agg_path.write_text(json.dumps(aggregate, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote %s (%s)" % (agg_path, ", ".join("%s %d" % kv for kv in counts.items())))


if __name__ == "__main__":
    main()
