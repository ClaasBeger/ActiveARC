#!/usr/bin/env python3
"""Render one or more ActiveARC agent trial JSON dumps as a self-contained HTML report."""

from __future__ import annotations

import argparse
import json
import sys
from html import escape
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from framework.active_arc.headless_trial import create_trial_session

COLORS = {
    0: "#000000",
    1: "#0068cf",
    2: "#ff3937",
    3: "#00c443",
    4: "#ffd631",
    5: "#a0a0a0",
    6: "#f916b1",
    7: "#ff7a2c",
    8: "#63d6fc",
    9: "#820f23",
}


def _grid_html(
    grid: Optional[List[List[int]]],
    title: str,
    *,
    highlight: Optional[Set[Tuple[int, int]]] = None,
) -> str:
    if not grid:
        return f"<div class='panel'><h4>{escape(title)}</h4><p class='muted'>n/a</p></div>"
    h = len(grid)
    w = len(grid[0]) if grid else 0
    cell = max(6, min(16, int(220 / max(h, w, 1))))
    rows: List[str] = []
    for r, row in enumerate(grid):
        tds: List[str] = []
        for c, val in enumerate(row):
            v = int(val)
            border = (
                "outline:2px solid #fff;outline-offset:-2px;"
                if highlight and (r, c) in highlight
                else ""
            )
            tds.append(
                f"<td style='width:{cell}px;height:{cell}px;background:{COLORS.get(v, '#333')};{border}' "
                f"title='({r},{c})={v}'></td>"
            )
        rows.append("<tr>" + "".join(tds) + "</tr>")
    return (
        f"<div class='panel'><h4>{escape(title)}</h4>"
        f"<div class='meta'>{h}×{w}</div>"
        f"<table class='grid'>{''.join(rows)}</table></div>"
    )


def _pair_html(inp: List[List[int]], out: List[List[int]], title: str) -> str:
    return (
        f"<div class='pair'><div class='pair-title'>{escape(title)}</div>"
        f"<div class='row'>{_grid_html(inp, 'Input')}{_grid_html(out, 'Output')}</div></div>"
    )


def _parse_tool_args(raw: str) -> Dict[str, Any]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_raw": raw}


def _turn_html(turn: Dict[str, Any]) -> str:
    n = turn.get("turn", "?")
    parts = [f"<section class='turn'><h3>Turn {n}</h3>"]
    if turn.get("assistant"):
        parts.append(f"<p class='assistant'>{escape(str(turn['assistant']))}</p>")
    calls = turn.get("tool_calls") or []
    results = turn.get("tool_results") or []
    for i, call in enumerate(calls):
        name = call.get("name", "?")
        args = _parse_tool_args(call.get("arguments") or "{}")
        parts.append(f"<div class='tool'><div class='tool-name'>{escape(name)}</div>")
        if name == "submit_query" and "grid" in args:
            parts.append("<div class='row'>" + _grid_html(args["grid"], "Query input") + "</div>")
        elif name == "submit_final_answer" and "grid" in args:
            parts.append("<div class='row'>" + _grid_html(args["grid"], "Submitted answer") + "</div>")
        elif name == "finish_exploration":
            parts.append("<p class='muted'>End exploration → test phase</p>")

        if i < len(results):
            res = results[i].get("result") or {}
            if name == "submit_query" and res.get("output_grid"):
                note = res.get("note", "")
                parts.append(
                    "<div class='row'>"
                    + _grid_html(res["output_grid"], f"Verifier output {note}".strip())
                    + "</div>"
                )
                if res.get("queried_shown_test_input"):
                    rnd = res.get("matched_test_round", "?")
                    parts.append(
                        f"<p class='note'>⚠ Queried a previously shown test input (round {rnd})</p>"
                    )
            elif name == "finish_exploration" and res.get("test_input_grid"):
                parts.append(
                    "<div class='row'>"
                    + _grid_html(res["test_input_grid"], "Test input (hidden output)")
                    + "</div>"
                )
            elif name == "submit_final_answer":
                if res.get("error"):
                    parts.append(f"<p class='err'>{escape(str(res['error']))}</p>")
                elif res.get("done"):
                    ok = res.get("correct")
                    label = "Correct" if ok else "Wrong"
                    cls = "ok" if ok else "bad"
                    parts.append(
                        f"<p class='{cls}'>{label} · query_count={res.get('query_count', '?')}</p>"
                    )
                elif res.get("correct") is False:
                    parts.append(
                        f"<p class='bad'>Wrong · query_count={res.get('query_count', '?')}"
                        f"{' · +10 penalty' if res.get('penalty_applied') else ''}</p>"
                    )
                    if res.get("message"):
                        parts.append(f"<p class='note'>{escape(str(res['message']))}</p>")
            elif res.get("message"):
                parts.append(f"<p class='note'>{escape(str(res['message']))}</p>")
            elif res.get("error"):
                parts.append(f"<p class='err'>{escape(str(res['error']))}</p>")
        parts.append("</div>")
    parts.append("</section>")
    return "\n".join(parts)


def _run_section(trial: Dict[str, Any], label: str) -> str:
    task_id = trial.get("task_id", "?")
    seed = trial.get("seed", "?")
    model = trial.get("model", "?")
    final = trial.get("final") or {}
    correct = final.get("correct", trial.get("correct"))
    if correct is True:
        result_label, status = "Correct", "correct"
    elif correct is False:
        result_label, status = "Wrong", "wrong"
    else:
        reason = final.get("reason", "?")
        result_label, status = f"Incomplete ({reason})", "incomplete"
    q = trial.get("query_count", final.get("query_count", "?"))
    turns = len(trial.get("transcript") or [])
    flags = trial.get("flags") or {}
    parts = [
        f"<section class='run {status}'>",
        f"<h2>{escape(label)}</h2>",
        "<ul class='summary'>",
        f"<li><strong>Task</strong> {escape(str(task_id))}</li>",
        f"<li><strong>Seed</strong> {escape(str(seed))}</li>",
        f"<li><strong>Model</strong> {escape(str(model))}</li>",
        f"<li><strong>Queries</strong> {escape(str(q))}</li>",
        f"<li><strong>Test-input queries</strong> {escape(str(trial.get('test_input_query_count', 0)))}</li>",
        f"<li><strong>API turns</strong> {turns}</li>",
        f"<li><strong>Result</strong> <span class='{status}'>{escape(result_label)}</span></li>",
    ]
    if final.get("message"):
        parts.append(f"<li><strong>Final message</strong> {escape(str(final['message']))}</li>")
    if flags:
        parts.append(f"<li><strong>Flags</strong> {escape(str(flags))}</li>")
    parts.append("</ul>")
    trial_ctx = trial.get("trial") or {}
    hs = trial_ctx.get("hot_start_pair")
    if hs and hs.get("input") and hs.get("output"):
        parts.append(
            _pair_html(hs["input"], hs["output"], "Hot-start example pair (shown to model)")
        )
    else:
        try:
            session = create_trial_session(seed=int(seed), task_id=str(task_id))
            hs2 = session.hot_start_json()
            if hs2:
                parts.append(
                    _pair_html(hs2["input"], hs2["output"], "Hot-start example pair (reconstructed)")
                )
        except Exception as e:
            parts.append(f"<p class='err'>Could not load hot-start: {escape(str(e))}</p>")
    for turn in trial.get("transcript") or []:
        parts.append(_turn_html(turn))
    parts.append("</section>")
    return "\n".join(parts)


def render_html(trials: List[Tuple[str, Dict[str, Any]]], title: str) -> str:
    body = "\n".join(_run_section(t, label) for label, t in trials)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{escape(title)}</title>
<style>
  :root {{ font-family: system-ui, sans-serif; background: #0f1115; color: #e8eaed; }}
  body {{ margin: 0; padding: 1.5rem 2rem 3rem; max-width: 1400px; }}
  h1 {{ margin-top: 0; font-size: 1.5rem; }}
  h2 {{ margin: 0 0 0.75rem; font-size: 1.2rem; }}
  h3 {{ margin: 1rem 0 0.5rem; font-size: 1rem; color: #9aa0a6; }}
  h4 {{ margin: 0 0 0.35rem; font-size: 0.85rem; font-weight: 600; }}
  .run {{ border: 1px solid #2a2f3a; border-radius: 10px; padding: 1rem 1.25rem 1.5rem; margin: 1.5rem 0; background: #161a22; }}
  .summary {{ margin: 0 0 1rem; padding-left: 1.2rem; color: #bdc1c6; }}
  .summary li {{ margin: 0.2rem 0; }}
  .pair {{ margin: 1rem 0; padding: 0.75rem; background: #1c212b; border-radius: 8px; }}
  .pair-title {{ font-weight: 600; margin-bottom: 0.5rem; color: #8ab4f8; }}
  .turn {{ margin-top: 1rem; padding-top: 0.5rem; border-top: 1px dashed #333; }}
  .tool {{ margin: 0.75rem 0; padding: 0.75rem; background: #12151c; border-radius: 8px; }}
  .tool-name {{ font-family: ui-monospace, monospace; color: #f28b82; margin-bottom: 0.5rem; }}
  .row {{ display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: flex-start; }}
  .panel {{ background: #0b0d11; padding: 0.5rem; border-radius: 6px; }}
  .meta {{ font-size: 0.75rem; color: #80868b; margin-bottom: 0.25rem; }}
  table.grid {{ border-collapse: collapse; }}
  table.grid td {{ border: 1px solid #222; }}
  .muted {{ color: #80868b; font-size: 0.9rem; }}
  .note {{ color: #fdd663; font-size: 0.9rem; }}
  .err {{ color: #f28b82; }}
  .ok, .correct {{ color: #81c995; }}
  .bad, .wrong {{ color: #f28b82; }}
  .incomplete {{ color: #fdd663; }}
  .lead {{ color: #9aa0a6; max-width: 70ch; line-height: 1.5; }}
</style>
</head>
<body>
<h1>{escape(title)}</h1>
<p class="lead">ARC grid colors: black=0, blue=1, red=2, green=3, yellow=4, gray=5, pink=6, orange=7, cyan=8, maroon=9.</p>
{body}
</body>
</html>
"""


def main() -> None:
    p = argparse.ArgumentParser(description="Render trial JSON transcript(s) as HTML")
    p.add_argument(
        "trials",
        nargs="+",
        metavar="LABEL=PATH",
        help="Trial dump as label=path/to/trial.json (repeat for comparison)",
    )
    p.add_argument("-o", "--output", type=Path, required=True)
    p.add_argument("--title", default="ActiveARC trial report")
    args = p.parse_args()

    loaded: List[Tuple[str, Dict[str, Any]]] = []
    for spec in args.trials:
        if "=" not in spec:
            raise SystemExit(f"Expected LABEL=PATH, got {spec!r}")
        label, path_s = spec.split("=", 1)
        path = Path(path_s)
        loaded.append((label, json.loads(path.read_text(encoding="utf-8"))))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_html(loaded, args.title), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
