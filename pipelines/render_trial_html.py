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
from framework.prompting.active_arc_tools import REQUEST_TEST_TOOL_NAMES

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


def _mismatch_cells(
    gold: Optional[List[List[int]]], pred: Optional[List[List[int]]]
) -> Set[Tuple[int, int]]:
    if not gold or not pred:
        return set()
    hits: Set[Tuple[int, int]] = set()
    for r, grow in enumerate(gold):
        prow = pred[r] if r < len(pred) else []
        for c, gv in enumerate(grow):
            pv = prow[c] if c < len(prow) else None
            if pv != gv:
                hits.add((r, c))
    if len(pred) != len(gold) or (pred and gold and len(pred[0]) != len(gold[0])):
        for r, prow in enumerate(pred):
            for c in range(len(prow)):
                hits.add((r, c))
    return hits


def _iq_section(trial: Dict[str, Any], label: str) -> str:
    task_id = trial.get("task_id", "?")
    exam_correct = trial.get("exam_correct")
    exam_n = trial.get("exam_n")
    n_show = trial.get("n_show_pair", len(trial.get("demonstrations") or []))
    n_probe = trial.get("n_query_student", len(trial.get("probes") or []))
    ok = trial.get("correct") is True
    status = "correct" if ok else "wrong"
    result_label = f"{exam_correct}/{exam_n} exam" if exam_n is not None else "exam"
    parts = [
        f"<section class='run {status}'>",
        f"<h2>{escape(label)}</h2>",
        "<ul class='summary'>",
        f"<li><strong>Task</strong> {escape(str(task_id))}</li>",
        f"<li><strong>Seed</strong> {escape(str(trial.get('seed', '?')))}</li>",
        f"<li><strong>Model</strong> {escape(str(trial.get('model', '?')))}</li>",
        f"<li><strong>Effort</strong> {escape(str(trial.get('reasoning_effort', '?')))}</li>",
        f"<li><strong>Shown pairs</strong> {escape(str(n_show))} "
        f"(example={trial.get('n_show_example', '?')}, "
        f"transformed={trial.get('n_show_transformed', '?')})</li>",
        f"<li><strong>Student probes</strong> {escape(str(n_probe))}</li>",
        f"<li><strong>Failed shows</strong> {escape(str(trial.get('n_failed_show', 0)))}</li>",
        f"<li><strong>Exam</strong> <span class='{status}'>{escape(str(result_label))}</span></li>",
    ]
    programs = trial.get("programs") or {}
    if programs.get("nl_rule"):
        parts.append(f"<li><strong>NL rule</strong> {escape(str(programs['nl_rule']))}</li>")
    if programs.get("verifier_slot"):
        parts.append(f"<li><strong>Verifier</strong> {escape(str(programs['verifier_slot']))}</li>")
    parts.append("</ul>")
    parts.append(
        "<p class='muted'><a href='#teacher-sample'>Teacher sample</a> · "
        "<a href='#shown'>Shown pairs</a> · <a href='#exam'>Exam</a></p>"
    )

    teacher_sample = trial.get("teacher_sample")
    parts.append("<h3 id='teacher-sample'>Teacher-only sample</h3>")
    if teacher_sample and teacher_sample.get("input") is not None:
        parts.append(
            _pair_html(
                teacher_sample.get("input") or [],
                teacher_sample.get("output") or [],
                "Not shown to the student unless the teacher later demonstrated it",
            )
        )
    else:
        parts.append("<p class='muted'>No teacher-only generator sample.</p>")

    demos = trial.get("demonstrations") or []
    parts.append(f"<h3 id='shown'>Shown pairs ({len(demos)})</h3>")
    if not demos:
        parts.append("<p class='muted'>No demonstrations.</p>")
    for i, demo in enumerate(demos, start=1):
        parts.append(
            _pair_html(demo.get("input") or [], demo.get("output") or [], f"Shown {i}/{len(demos)}")
        )

    probes = trial.get("probes") or []
    if probes:
        parts.append(f"<h3>Student probes ({len(probes)})</h3>")
        for i, probe in enumerate(probes, start=1):
            pred = probe.get("prediction")
            gold = probe.get("gold_output") or probe.get("output")
            title = f"Probe {i}/{len(probes)}"
            if gold is not None:
                parts.append(_pair_html(probe.get("input") or [], gold, title + " (gold)"))
            if pred is not None:
                parts.append(_pair_html(probe.get("input") or [], pred, title + " (student)"))

    exam = trial.get("exam") or []
    parts.append(f"<h3 id='exam'>Exam ({exam_correct}/{exam_n})</h3>")
    for i, item in enumerate(exam, start=1):
        pred = item.get("prediction")
        gold = item.get("gold_output")
        inp = item.get("input")
        item_ok = item.get("correct") is True
        cls = "ok" if item_ok else "bad"
        label_i = "correct" if item_ok else "wrong"
        hi = _mismatch_cells(gold, pred)
        extra = f" · {len(hi)} cell mismatch" if hi else ""
        parts.append(f"<div class='pair exam-item {cls}'>")
        parts.append(
            f"<div class='pair-title'>Exam {i}/{len(exam)} · "
            f"<span class='{cls}'>{label_i}</span>{escape(extra)}</div>"
        )
        parts.append("<div class='row'>")
        parts.append(_grid_html(inp, "Exam input"))
        parts.append(_grid_html(gold, "Gold output"))
        parts.append(_grid_html(pred, "Student prediction", highlight=hi or None))
        parts.append("</div></div>")

    parts.append("</section>")
    return "\n".join(parts)


def _load_task_for_trial(trial: Dict[str, Any]):
    """Load the ArcTask a trial ran on (dataset-aware)."""
    dataset = trial.get("dataset", "arc")
    task_id = str(trial.get("task_id"))
    if dataset == "parc":
        from framework.tasks.parc_dataset import load_parc_task

        return load_parc_task(task_id)
    if dataset == "conceptarc":
        from framework.integrations.conceptarc_adapter import load_conceptarc_task

        return load_conceptarc_task(task_id)
    from framework.tasks.arc_dataset import load_task

    return load_task(task_id, load_alternative_verifiers=False)


def _recorded_pairs(trial: Dict[str, Any]) -> List[Tuple[List[List[int]], List[List[int]]]]:
    """Input/output pairs the model actually saw (hot start + queries)."""
    if (trial.get("flags") or {}).get("noisy_science"):
        return []
    ctx = trial.get("trial") or {}
    pairs: List[Tuple[List[List[int]], List[List[int]]]] = []
    hs = ctx.get("hot_start_pair")
    if hs and hs.get("input") and hs.get("output"):
        pairs.append((hs["input"], hs["output"]))
    for h in ctx.get("query_history") or []:
        if h.get("input") and h.get("output"):
            pairs.append((h["input"], h["output"]))
    return pairs


def _verifier_reproduces(fn, pairs) -> bool:
    import copy as _copy

    for inp, out in pairs:
        try:
            if fn(_copy.deepcopy(inp)) != out:
                return False
        except Exception:
            return False
    return True


def _resolve_trial_verifier(trial: Dict[str, Any]):
    """The exact verifier callable this trial used.

    A slot name is not a unique key (ARC-AGI-2 exposes several under "custom"),
    so candidates for the recorded slot are disambiguated by replaying the
    outputs the model was actually shown.
    """
    task = _load_task_for_trial(trial)
    dataset = trial.get("dataset", "arc")
    if dataset in ("parc", "conceptarc"):
        return task.quinary_verifier or task.verifier
    from framework.active_arc.verifier_selection import list_valid_verifiers

    slot = (trial.get("trial") or {}).get("verifier_slot")
    candidates = list_valid_verifiers(task)
    same_slot = [fn for s, fn in candidates if s == slot]
    pairs = _recorded_pairs(trial)
    if pairs:
        for fn in same_slot or [fn for _, fn in candidates]:
            if _verifier_reproduces(fn, pairs):
                return fn
    if same_slot:
        return same_slot[0]
    return candidates[0][1] if candidates else None


def _gold_test_output(trial: Dict[str, Any]) -> Optional[List[List[int]]]:
    import copy as _copy

    test_input = (trial.get("trial") or {}).get("test_input")
    if not test_input:
        return None
    fn = _resolve_trial_verifier(trial)
    if fn is None:
        return None
    out = fn(_copy.deepcopy(test_input))
    return [[int(c) for c in row] for row in out]


def _submitted_answer(trial: Dict[str, Any]) -> Optional[List[List[int]]]:
    grid = None
    for turn in trial.get("transcript") or []:
        for call in turn.get("tool_calls") or []:
            if call.get("name") == "submit_final_answer":
                args = _parse_tool_args(call.get("arguments") or "{}")
                if isinstance(args.get("grid"), list):
                    grid = args["grid"]
    return grid


def _ground_truth_rule(trial: Dict[str, Any]) -> Optional[Tuple[str, str, List[Tuple[str, str]]]]:
    """Return ``(kind, summary, [(source label, source text)])`` for the true rule."""
    dataset = trial.get("dataset", "arc")
    task_id = str(trial.get("task_id"))
    if dataset in ("arc", "arc2"):
        from framework.integrations.nl_rules import larc_rule, marc2_rule

        rule = larc_rule(task_id) if dataset == "arc" else marc2_rule(task_id)
        if rule:
            kind = "LARC natural-language rule" if dataset == "arc" else "MARC2 natural-language rule"
            return kind, rule, []
        return None
    if dataset == "parc":
        from framework.tasks.parc_dataset import parc_source_paths

        gen_path, ver_path = parc_source_paths(task_id)
        summary = gen_path.parent.name.replace("_", " ")
        sources: List[Tuple[str, str]] = []
        for path in (ver_path, gen_path):
            try:
                sources.append((path.name, path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return "reference implementation", summary, sources
    return None


def _ground_truth_html(trial: Dict[str, Any]) -> str:
    """Test input, true output, submitted answer (mismatches outlined), and the rule."""
    parts: List[str] = []
    ctx = trial.get("trial") or {}
    test_input = ctx.get("test_input")
    gold: Optional[List[List[int]]] = None
    err: Optional[str] = None
    try:
        gold = _gold_test_output(trial)
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
    pred = _submitted_answer(trial)
    if test_input or gold or pred:
        highlight = _mismatch_cells(gold, pred)
        n_diff = len(highlight)
        head = "Ground truth vs submitted answer"
        if gold and pred:
            total = len(gold) * len(gold[0]) if gold and gold[0] else 0
            head += f" — {n_diff} of {total} cells differ" if n_diff else " — exact match"
        parts.append(f"<div class='pair'><div class='pair-title'>{escape(head)}</div><div class='row'>")
        parts.append(_grid_html(test_input, "Test input"))
        parts.append(_grid_html(gold, "Ground-truth output"))
        parts.append(_grid_html(pred, "Submitted answer", highlight=highlight))
        parts.append("</div>")
        if err:
            parts.append(f"<p class='err'>Could not compute ground truth: {escape(err)}</p>")
        parts.append("</div>")
    rule = None
    try:
        rule = _ground_truth_rule(trial)
    except Exception as e:
        parts.append(f"<p class='err'>Could not load rule: {escape(str(e))}</p>")
    if rule:
        kind, summary, sources = rule
        parts.append(
            f"<div class='pair'><div class='pair-title'>Ground-truth rule ({escape(kind)})</div>"
            f"<p class='rule'>{escape(summary)}</p>"
        )
        for name, text in sources:
            parts.append(
                f"<details><summary>{escape(name)} ({len(text.splitlines())} lines)</summary>"
                f"<pre class='src'>{escape(text)}</pre></details>"
            )
        parts.append("</div>")
    return "\n".join(parts)


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
        elif name in REQUEST_TEST_TOOL_NAMES:
            parts.append("<p class='muted'>Request test → test phase</p>")

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
            elif name in REQUEST_TEST_TOOL_NAMES and res.get("test_input_grid"):
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
                    extra = ""
                    if not ok and res.get("penalty_applied"):
                        extra = f" · +{res.get('penalty', '?')} penalty"
                    parts.append(
                        f"<p class='{cls}'>{label} · query_count={res.get('query_count', '?')}{extra}</p>"
                    )
                elif res.get("correct") is False:
                    parts.append(
                        f"<p class='bad'>Wrong · query_count={res.get('query_count', '?')}"
                        f"{' · +' + str(res.get('penalty', 10)) + ' penalty' if res.get('penalty_applied') else ''}</p>"
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


def _run_section(trial: Dict[str, Any], label: str, *, with_ground_truth: bool = True) -> str:
    if trial.get("setting") == "inverse_query":
        return _iq_section(trial, label)
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
    if with_ground_truth:
        parts.append(_ground_truth_html(trial))
    for turn in trial.get("transcript") or []:
        parts.append(_turn_html(turn))
    parts.append("</section>")
    return "\n".join(parts)


def render_html(
    trials: List[Tuple[str, Dict[str, Any]]],
    title: str,
    *,
    with_ground_truth: bool = True,
) -> str:
    body = "\n".join(
        _run_section(t, label, with_ground_truth=with_ground_truth) for label, t in trials
    )
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
  .rule {{ margin: 0.25rem 0 0.5rem; color: #e8eaed; white-space: pre-wrap; }}
  details {{ margin-top: 0.5rem; }}
  summary {{ cursor: pointer; color: #8ab4f8; font-size: 0.85rem; }}
  .src {{ background: #0b0d11; padding: 0.75rem; border-radius: 6px; overflow-x: auto;
          font-size: 0.75rem; line-height: 1.35; max-height: 32rem; }}
  table.grid {{ border-collapse: collapse; }}
  table.grid td {{ border: 1px solid #222; }}
  .muted {{ color: #80868b; font-size: 0.9rem; }}
  .note {{ color: #fdd663; font-size: 0.9rem; }}
  .err {{ color: #f28b82; }}
  .ok, .correct {{ color: #81c995; }}
  .bad, .wrong {{ color: #f28b82; }}
  .incomplete {{ color: #fdd663; }}
  .lead {{ color: #9aa0a6; max-width: 70ch; line-height: 1.5; }}
  a {{ color: #8ab4f8; }}
  .exam-item.ok {{ border-left: 3px solid #81c995; }}
  .exam-item.bad {{ border-left: 3px solid #f28b82; }}
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
    p.add_argument(
        "--ground-truth",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include the true test output (re-run through the trial verifier) and the "
        "ground-truth rule. On by default; --no-ground-truth to omit.",
    )
    args = p.parse_args()

    loaded: List[Tuple[str, Dict[str, Any]]] = []
    for spec in args.trials:
        if "=" not in spec:
            raise SystemExit(f"Expected LABEL=PATH, got {spec!r}")
        label, path_s = spec.split("=", 1)
        path = Path(path_s)
        loaded.append((label, json.loads(path.read_text(encoding="utf-8"))))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        render_html(loaded, args.title, with_ground_truth=args.ground_truth),
        encoding="utf-8",
    )
    print(args.output)


if __name__ == "__main__":
    main()
