#!/usr/bin/env python3
"""An annotation worksheet for the rules nobody has written yet.

``python -m pipelines.build_missing_rule_worksheet``

Lists every ARC-AGI-1 / ARC-AGI-2 task that still has no natural-language rule
(neither a published lookup nor a draft), grouped by whoever it is assigned to,
with the official train pairs and the test input drawn out and a copy-ready
skeleton underneath.  The two datasets get different skeletons because their
published rules are shaped differently: LARC's 364 entries all use the same
three-clause form, MARC2's are free prose in three paragraphs.

Writes ``experiments/nl_rule_worksheet.html``.
"""

from __future__ import annotations

import html
import sys
from pathlib import Path
from typing import Dict, List

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from pipelines.build_nl_rule_report import assignments, collect, drafts  # noqa: E402
from pipelines.render_trial_html import _grid_html  # noqa: E402

OUT = ROOT_DIR / "experiments" / "nl_rule_worksheet.html"

SKELETON = {
    "ARC-AGI-1": (
        "In the input, you should see...\n\n"
        "The output grid size...\n\n"
        "To make the output, you have to..."
    ),
    # Measured on the 168 MARC2 rules, not guessed: 164 are exactly three
    # paragraphs, 159 open by describing the input, 145 state the transformation
    # in the second, and 164 give the grid's dimensions in the third (134 also
    # name the background). The third paragraph is grid properties -- what holds
    # of both grids -- rather than a description of the output alone.
    "ARC-AGI-2": (
        "<the input: its objects, their colours, the background, and what always "
        "holds of them>\n\n"
        "<the transformation, stated so someone could carry it out without seeing "
        "the examples>\n\n"
        "<grid properties: the dimensions of input and output, the background "
        "colour, and what is left unchanged>"
    ),
}

VIEWER = {
    "ARC-AGI-1": "https://arcprize.org/play?task=%s",
    "ARC-AGI-2": "https://arcprize.org/play?task=%s",
}

CSS = """
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:0;
padding:24px 28px;background:#faf9f7;color:#1d1c1a;line-height:1.5}
h1{font-size:21px;margin:0 0 6px}
h2{font-size:17px;margin:30px 0 4px;border-bottom:2px solid #e2dfd9;padding-bottom:5px}
h4{font-size:11px;margin:0 0 3px;font-weight:600;color:#6b6862;text-transform:uppercase;
letter-spacing:.04em}
.sub{color:#6b6862;font-size:13px;max-width:94ch;margin-bottom:14px}
.task{background:#fff;border:1px solid #e6e3dd;border-radius:6px;padding:14px 16px;
margin:14px 0;box-shadow:0 1px 2px rgba(0,0,0,.05)}
.hdr{display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap}
.tid{font-family:ui-monospace,Menlo,monospace;font-size:15px;font-weight:600}
.badge{background:#e8f0fb;color:#1d4e89;border-radius:10px;padding:1px 9px;font-size:12px}
.badge.ds{background:#f0eae8;color:#7a4b3a}
.row{display:flex;gap:14px;flex-wrap:wrap;align-items:flex-start;margin-bottom:8px}
.pair{display:flex;gap:8px;align-items:flex-start;background:#fbfaf8;border:1px solid #efece7;
border-radius:5px;padding:8px}
.panel .meta{font-size:10px;color:#8b8880;margin-bottom:2px}
table.grid{border-collapse:collapse;border:1px solid #3a3a3a}
table.grid td{padding:0;border:1px solid #2a2a2a}
textarea{width:100%;box-sizing:border-box;font-family:ui-monospace,Menlo,monospace;
font-size:12px;padding:8px 10px;border:1px solid #dcd8d1;border-radius:4px;background:#fdfcfa;
line-height:1.5;color:#43403b}
.muted{color:#8b8880;font-size:12px}
.toc{background:#fff;border:1px solid #e6e3dd;border-radius:6px;padding:10px 14px;
display:inline-block;font-size:13px}
details summary{cursor:pointer;margin:4px 0 6px}
.toc code{background:#f0eee9;padding:1px 5px;border-radius:3px;margin-right:4px}
a{color:#1d4e89}
.bar{position:fixed;right:18px;bottom:18px;background:#fff;border:1px solid #d9d5cd;
border-radius:8px;padding:10px 14px;box-shadow:0 4px 14px rgba(0,0,0,.14);font-size:13px;z-index:9}
.bar button{font:inherit;padding:5px 11px;margin-left:7px;border:1px solid #c8c3ba;
border-radius:5px;background:#f7f5f1;cursor:pointer}
.bar button:hover{background:#eeebe5}
.task.done{border-color:#b6d3b6;background:#fcfefc}
.task.done .tid::after{content:' \2713';color:#3f8b3f}
#dump{width:100%;height:34vh;margin-top:9px;display:none}
"""


SCRIPT = r"""
<div class='bar'>
  <b id='count'></b>
  <button onclick='save()'>Save .json</button>
  <button onclick='dump()'>Show all</button>
  <button onclick='reset()' title='Clear every field back to the skeleton'>Reset</button>
  <textarea id='dump' spellcheck='false'></textarea>
</div>
<script>
// Typed rules live in this browser's localStorage, so closing the tab or
// reopening a rebuilt worksheet does not lose them. "Save .json" writes the
// filled ones out in the shape external/nl_rules/ wants.
var KEY = 'nl_rule_worksheet';
var boxes = Array.prototype.slice.call(document.querySelectorAll('textarea[data-task]'));
function store(){ try { return JSON.parse(localStorage.getItem(KEY) || '{}'); } catch(e){ return {}; } }
var SKELETONS = {};
boxesInit();
function boxesInit(){
  document.querySelectorAll('textarea[data-skeleton]').forEach(function(b){
    SKELETONS[b.dataset.skeleton.trim()] = 1;
  });
}
function filled(b){ var v = b.value.trim(); return v && !SKELETONS[v] ? v : null; }
function grow(b){ b.style.height = 'auto'; b.style.height = (b.scrollHeight + 4) + 'px'; }
function tally(){
  var n = 0;
  boxes.forEach(function(b){
    var ok = !!filled(b);
    if (ok) n++;
    b.closest('.task').classList.toggle('done', ok);
  });
  document.getElementById('count').textContent = n + ' / ' + boxes.length;
}
var saved = store();
boxes.forEach(function(b){
  if (saved[b.dataset.task]) b.value = saved[b.dataset.task];
  grow(b);
  b.addEventListener('input', function(){
    var s = store();
    var v = filled(b);
    if (v) s[b.dataset.task] = b.value; else delete s[b.dataset.task];
    try { localStorage.setItem(KEY, JSON.stringify(s)); } catch(e){}
    grow(b); tally();
  });
});
tally();
function collected(){
  var out = {};
  boxes.forEach(function(b){ var v = filled(b); if (v) out[b.dataset.task] = v; });
  return out;
}
function save(){
  var blob = new Blob([JSON.stringify(collected(), null, 1)], {type:'application/json'});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'nl_rule_worksheet.json';
  a.click();
}
function dump(){
  var t = document.getElementById('dump'), c = collected();
  var text = Object.keys(c).map(function(k){ return '=== ' + k + '\n' + c[k]; }).join('\n\n');
  if (t.style.display === 'block' ) { t.style.display = 'none'; return; }
  t.value = text; t.style.display = 'block'; t.focus(); t.select();
}
function reset(){
  if (!confirm('Clear every field?')) return;
  try { localStorage.removeItem(KEY); } catch(e){}
  boxes.forEach(function(b){ b.value = b.dataset.skeleton; grow(b); });
  tally();
}
</script>
"""


def _tasks_missing() -> List[Dict[str, str]]:
    data = collect()
    who = assignments()
    draft = drafts()
    owner = {(ds, t): name for name, sets in who.items()
             for ds, ids in sets.items() for t in ids}
    out: List[Dict[str, str]] = []
    for ds in ("ARC-AGI-1", "ARC-AGI-2"):
        for tid, rule in data[ds]["rules"].items():  # type: ignore[index]
            if rule or tid in draft:
                continue
            out.append({"dataset": ds, "task_id": tid,
                        "owner": owner.get((ds, tid), "unassigned")})
    return out


def _task_html(entry: Dict[str, str]) -> str:
    from framework.tasks.arc_dataset import load_task

    tid, ds = entry["task_id"], entry["dataset"]
    task = load_task(tid, load_alternative_verifiers=False)
    parts = ["<div class='task' id='%s'>" % tid,
             "<div class='hdr'><span class='tid'>%s</span>"
             "<span class='badge ds'>%s</span><span class='badge'>%s</span>"
             "<a class='muted' href='%s' target='_blank'>open in the viewer</a></div>" % (
                 tid, ds, html.escape(entry["owner"]), VIEWER[ds] % tid)]
    parts.append("<div class='row'>")
    for i, pair in enumerate(task.train_pairs):
        parts.append("<div class='pair'>%s%s</div>" % (
            _grid_html(pair.input, "train %d in" % i),
            _grid_html(pair.output, "train %d out" % i)))
    for i, inp in enumerate(task.test_inputs):
        parts.append("<div class='pair'>%s</div>" % _grid_html(inp, "test %d in" % i))
    parts.append("</div>")
    # The test output is what a rule has to be good enough to reconstruct, so it
    # is here to check against -- folded away, since reading it first is the one
    # way to end up describing the answer instead of the rule.
    if task.test_outputs:
        parts.append("<details><summary class='muted'>test output</summary><div class='row'>")
        for i, out in enumerate(task.test_outputs):
            parts.append("<div class='pair'>%s</div>" % _grid_html(out, "test %d out" % i))
        parts.append("</div></details>")
    skeleton = SKELETON[ds]
    parts.append("<h4>rule</h4><textarea rows='%d' spellcheck='false' data-task='%s' "
                 "data-skeleton='%s'>%s</textarea>" % (
                     7 if ds == "ARC-AGI-1" else 8, tid,
                     html.escape(skeleton), html.escape(skeleton)))
    parts.append("</div>")
    return "".join(parts)


def main() -> None:
    entries = _tasks_missing()
    by_owner: Dict[str, List[Dict[str, str]]] = {}
    for e in entries:
        by_owner.setdefault(e["owner"], []).append(e)

    p = ["<meta charset=\"utf-8\"><style>%s</style>" % CSS,
         "<h1>Rules still to write &mdash; %d tasks</h1>" % len(entries),
         "<div class='sub'>Every ARC-AGI-1 and ARC-AGI-2 task with no rule on file and no draft. "
         "The skeleton under each task is the shape its dataset's own rules use: ARC-AGI-1 follows "
         "LARC's three clauses (all 364 published entries do), ARC-AGI-2 follows MARC2's three "
         "paragraphs of free prose. Grids are the official train pairs and test input &mdash; hover "
         "a cell for its coordinates and colour.</div>"]
    for owner in sorted(by_owner):
        ids = by_owner[owner]
        p.append("<div class='toc'><b>%s</b> &mdash; %s</div>" % (
            html.escape(owner),
            " ".join("<a href='#%s'><code>%s</code></a>" % (e["task_id"], e["task_id"])
                     for e in ids)))
    for owner in sorted(by_owner):
        p.append("<h2>%s &mdash; %d</h2>" % (html.escape(owner), len(by_owner[owner])))
        for ds in ("ARC-AGI-1", "ARC-AGI-2"):
            for e in by_owner[owner]:
                if e["dataset"] == ds:
                    p.append(_task_html(e))
    p.append(SCRIPT)
    OUT.write_text("".join(p), encoding="utf-8")
    print("wrote %s (%.0f KB, %d tasks)" % (OUT, OUT.stat().st_size / 1024, len(entries)))


if __name__ == "__main__":
    main()
