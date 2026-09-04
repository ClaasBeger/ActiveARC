from __future__ import annotations

import argparse
import copy
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from framework.active_arc.headless_trial import create_trial_session
from framework.active_arc.query_noise import maybe_corrupt_query_output
from framework.active_arc.verifier_selection import (
    list_valid_verifiers,
    sample_consistent_dynamic_pair,
)
from framework.integrations.conceptarc_adapter import list_conceptarc_task_ids
from framework.integrations.agi2_verifiers import list_agi2_valid_task_ids
from framework.tasks.parc_dataset import list_parc_task_ids
from framework.dimensions.classification_distribution import VerifierSlot
from framework.grids import Grid, GridPair, clone_grid, is_equal_grid, validate_grid
from framework.tasks.base import ArcTask, Verifier
from interface.arc_grid_editor import arc_grid_editor, arc_grid_editor_available
from interface.render import grid_height_px, grid_html


Phase = Literal["explore", "test", "done"]


def _parse_cli() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="ActiveARC query–test interface")
    p.add_argument(
        "--hot-start",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Show one random generator example pair for free (no query cost). On by default; use --no-hot-start to disable.",
    )
    p.add_argument(
        "--noisy-science",
        action="store_true",
        help="Randomly corrupt each query output (see --noise-probability). Combinable.",
    )
    p.add_argument(
        "--re-trials",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Wrong final test answer returns to exploration and adds +10 to query count. On by default; use --no-re-trials to disable.",
    )
    p.add_argument(
        "--mode",
        choices=["standard", "hot_start", "noisy_science", "re_trials"],
        default=None,
        help="Legacy alias for a single feature (OR-combined with --hot-start / --noisy-science / --re-trials).",
    )
    p.add_argument(
        "--fixed-test",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Keep one test sample for the whole trial (default: resample on each finish_exploration).",
    )
    p.add_argument(
        "--noise-probability",
        type=float,
        default=0.12,
        help="Used with --noisy-science: probability each query output is corrupted (clamped to 0.05–0.20).",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=None,
        help="RNG seed for task/verifier selection and trials.",
    )
    p.add_argument(
        "--task-id",
        type=str,
        default=None,
        help=(
            "Task id (ARC-AGI-1/2: 8eb1be9a or 00576224; ConceptARC: count/count11; "
            "P-ARC: test2_t1 or t1). "
            "ConceptARC also accepts sample, sample/<concept>, or <concept>/sample "
            "to invent a new DSL family online."
        ),
    )
    p.add_argument(
        "--dataset",
        choices=["arc", "arc2", "conceptarc", "parc"],
        default="arc",
        help=(
            "Task pool: arc (ARC-AGI-1 training, default), arc2 (validated ARC-AGI-2), "
            "conceptarc (ConceptARC DSL), or parc (P-ARC)."
        ),
    )
    p.add_argument(
        "--sample-family",
        action="store_true",
        help="ConceptARC only: sample a new DSL task family online (same as --task-id sample).",
    )
    p.add_argument(
        "--persist-sampled-family",
        action="store_true",
        help="ConceptARC only: write a newly sampled family into the exported program catalog.",
    )
    return p.parse_known_args()[0]


def _feature_flags(args: argparse.Namespace) -> Tuple[bool, bool, bool]:
    """Return (hot_start, noisy_science, re_trials); flags and legacy --mode are OR-combined."""
    mode = getattr(args, "mode", None)
    hot = bool(args.hot_start) or mode == "hot_start"
    noisy = bool(args.noisy_science) or mode == "noisy_science"
    retrial = bool(args.re_trials) or mode == "re_trials"
    return hot, noisy, retrial


def _mode_caption(hot: bool, noisy: bool, retrial: bool) -> str:
    if not hot and not noisy and not retrial:
        return "baseline"
    parts: List[str] = []
    if hot:
        parts.append("hot_start")
    if noisy:
        parts.append("noisy_science")
    if retrial:
        parts.append("re_trials")
    return " + ".join(parts)


def _resize_grid(grid: Grid, height: int, width: int, fill: int = 0) -> Grid:
    out: Grid = []
    for r in range(height):
        row: List[int] = []
        for c in range(width):
            if r < len(grid) and c < len(grid[0]):
                row.append(int(grid[r][c]))
            else:
                row.append(fill)
        out.append(row)
    return out


_DEFAULT_QUERY_H = 5
_DEFAULT_QUERY_W = 5


def _bump_query_editor() -> None:
    """Increment nonce so the arc grid component remounts (Python-driven grid changes are applied)."""
    st.session_state.query_editor_nonce = int(st.session_state.get("query_editor_nonce", 0)) + 1


def _bump_test_editor() -> None:
    """Increment nonce so the test answer editor remounts after programmatic grid changes."""
    st.session_state.test_editor_nonce = int(st.session_state.get("test_editor_nonce", 0)) + 1
    # One-shot: ignore the remounted widget's first return so it cannot overwrite
    # the Python-assigned grid (Streamlit custom components often echo defaults).
    st.session_state._test_editor_force_grid = True


def _default_query_editor_blank() -> None:
    """Reset the exploration query editor to the initial empty grid."""
    st.session_state.query_h = _DEFAULT_QUERY_H
    st.session_state.query_w = _DEFAULT_QUERY_W
    st.session_state.query_grid = _resize_grid(
        [[0] * _DEFAULT_QUERY_W for _ in range(_DEFAULT_QUERY_H)],
        _DEFAULT_QUERY_H,
        _DEFAULT_QUERY_W,
    )
    _bump_query_editor()


def _normalize_grid_cells(grid: Grid) -> Grid:
    """Coerce every cell to int 0–9 (fixes JSON floats / component quirks)."""
    out: Grid = []
    for row in grid:
        out.append(
            [max(0, min(9, int(round(float(c))))) for c in row]
        )
    return out


def _session_valid_verifiers() -> List[Tuple[VerifierSlot, Verifier]]:
    task: ArcTask = st.session_state.task
    v = st.session_state.get("valid_verifiers")
    if v is not None and len(v) > 0:
        return v
    fresh = list_valid_verifiers(task)
    st.session_state.valid_verifiers = fresh
    return fresh


def _ordered_verifier_chain() -> List[Tuple[VerifierSlot, Verifier]]:
    """Primary (trial) verifier first, then other valid verifiers as fallbacks."""
    primary: VerifierSlot = st.session_state.verifier_slot
    valid = _session_valid_verifiers()
    first = [(s, f) for s, f in valid if s == primary]
    rest = [(s, f) for s, f in valid if s != primary]
    return first + rest


def _trial_verifier() -> Optional[Verifier]:
    verifier = st.session_state.get("verifier")
    if verifier is not None:
        return verifier
    chain = _session_valid_verifiers()
    return chain[0][1] if chain else None


def _ensure_test_pair() -> bool:
    """Sample a live generator test pair unless a fixed test is already held.

    Streamlit trials default to ``fixed_test=False``, so ``create_trial_session``
    leaves ``test_pair`` as ``None`` and the pair is drawn when exploration ends
    (same as ``ActiveArcTrialSession.finish_exploration``).
    """
    fixed = bool(st.session_state.get("fixed_test", False))
    existing = st.session_state.get("test_pair")
    if fixed and existing is not None:
        return True

    verifier = _trial_verifier()
    if verifier is None:
        return False

    exclude: List[Grid] = []
    hot = st.session_state.get("hot_start_pair")
    if hot is not None:
        exclude.append(hot.input)
    for prev in st.session_state.get("shown_test_inputs") or []:
        exclude.append(prev)

    pair = sample_consistent_dynamic_pair(
        st.session_state.task,
        verifier,
        st.session_state.rng,
        exclude_inputs=exclude or None,
    )
    if pair is None:
        return False
    st.session_state.test_pair = pair
    shown = list(st.session_state.get("shown_test_inputs") or [])
    shown.append(clone_grid(pair.input))
    st.session_state.shown_test_inputs = shown
    return True


def _run_verifier_chain(inp: Grid) -> Tuple[Grid, VerifierSlot]:
    """Return (output_grid, slot_used). Raises RuntimeError if every verifier fails."""
    errors: List[str] = []
    for slot, vfn in _ordered_verifier_chain():
        try:
            out = vfn(copy.deepcopy(inp))
            return clone_grid(out), slot
        except Exception as e:
            errors.append(f"{slot}: {type(e).__name__}: {e}")
    raise RuntimeError(
        "Every verifier failed on this input:\n" + "\n".join(errors)
    )


def _df_from_grid(g: Grid) -> pd.DataFrame:
    return pd.DataFrame(g, dtype="int64")


def _grid_from_df(df: pd.DataFrame) -> Grid:
    return df.fillna(0).round().astype(int).values.tolist()


def _arc_column_config(df: pd.DataFrame) -> Dict[Any, Any]:
    return {
        c: st.column_config.NumberColumn(min_value=0, max_value=9, step=1)
        for c in df.columns
    }


def _init_trial(
    args: argparse.Namespace,
    *,
    seed_override: Optional[int] = None,
    dataset_override: Optional[str] = None,
    task_id_override: Optional[str] = None,
    clear_task_id: bool = False,
) -> None:
    seed = (
        seed_override
        if seed_override is not None
        else (args.seed if args.seed is not None else random.randint(1, 2**31 - 1))
    )

    hot_start, noisy_science, re_trials = _feature_flags(args)
    noise_p = float(args.noise_probability)

    dataset = dataset_override or st.session_state.get("dataset") or args.dataset
    if task_id_override is not None:
        task_id = task_id_override
    elif clear_task_id:
        task_id = None
    else:
        task_id = args.task_id

    try:
        session = create_trial_session(
            seed=seed,
            task_id=task_id,
            hot_start=hot_start,
            noisy_science=noisy_science,
            re_trials=re_trials,
            fixed_test=bool(getattr(args, "fixed_test", False)),
            noise_probability=noise_p,
            dataset=dataset,
            sample_family=bool(getattr(args, "sample_family", False)),
            persist_sampled_family=bool(getattr(args, "persist_sampled_family", False)),
        )
    except ValueError as e:
        st.error(str(e))
        st.stop()
    except RuntimeError as e:
        st.error(str(e))
        st.stop()

    verifier: Optional[Verifier] = None
    for slot, vfn in session.valid_verifiers:
        if slot == session.verifier_slot:
            verifier = vfn
            break

    st.session_state.dataset = session.dataset
    st.session_state.trial_seed = session.seed
    st.session_state.rng = session.rng
    st.session_state.hot_start = session.hot_start
    st.session_state.noisy_science = session.noisy_science
    st.session_state.re_trials = session.re_trials
    st.session_state.noise_probability = session.noise_probability
    st.session_state.task_id = session.task_id
    st.session_state.task = session.task
    st.session_state.verifier_slot = session.verifier_slot
    st.session_state.verifier = verifier
    st.session_state.valid_verifiers = session.valid_verifiers
    st.session_state.hot_start_pair = session.hot_start_pair
    st.session_state.test_pair = session.test_pair
    st.session_state.fixed_test = session.fixed_test
    st.session_state.shown_test_inputs = []
    n_valid = len(session.valid_verifiers)
    st.session_state.phase = "explore"
    st.session_state.query_count = 0
    st.session_state.history = []
    _default_query_editor_blank()
    st.session_state.test_answer_grid = _resize_grid([[0] * 5 for _ in range(5)], 5, 5)
    st.session_state.test_h = 5
    st.session_state.test_w = 5
    st.session_state.test_correct = None
    st.session_state.n_valid_verifiers = n_valid
    st.session_state.re_trials_penalty_notice = False


def _render_grid_ui(grid: Grid, *, title: str, max_px: int) -> None:
    h = grid_height_px(grid, max_px=max_px)
    st.components.v1.html(grid_html(grid, title=title, max_px=max_px), height=h)


def _render_query_history_rows() -> None:
    hist: List[Dict[str, Any]] = st.session_state.history
    if not hist:
        return
    for i, row in enumerate(hist):
        c1, c2, c3 = st.columns([1, 0.12, 1])
        with c1:
            _render_grid_ui(row["input"], title=f"Q{i+1} in", max_px=11)
        with c2:
            st.markdown("<div style='margin-top:2rem;text-align:center'>→</div>", unsafe_allow_html=True)
        with c3:
            note = row.get("note", "")
            out_title = f"Q{i+1} out {note}"
            _render_grid_ui(row["output"], title=out_title, max_px=11)
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)


def _render_history_section(*, title: str) -> None:
    st.markdown(f"##### {title}")
    st.caption("Earlier input→output pairs (smaller thumbnails).")
    _render_query_history_rows()


def _render_hot_start_reference(*, max_px: int = 18) -> None:
    """Show the free hot-start example pair when hot_start is on (exploration and test)."""
    if not st.session_state.get("hot_start") or st.session_state.hot_start_pair is None:
        return
    st.info(
        "Hot start: one randomly chosen training input–output pair is shown below "
        "at no query cost (does not increase your query count)."
    )
    hp: GridPair = st.session_state.hot_start_pair
    c1, c2, c3 = st.columns([1, 0.15, 1])
    with c1:
        _render_grid_ui(hp.input, title="Free train input", max_px=max_px)
    with c2:
        st.markdown("<div style='margin-top:3rem;font-size:1.4rem'>→</div>", unsafe_allow_html=True)
    with c3:
        _render_grid_ui(hp.output, title="Free train output", max_px=max_px)


def _explore_phase() -> None:
    task = st.session_state.task
    task_id = st.session_state.task_id
    rng: random.Random = st.session_state.rng
    hot_start = st.session_state.hot_start
    noisy_science = st.session_state.noisy_science

    if st.session_state.get("re_trials_penalty_notice"):
        st.warning(
            "Incorrect test answer: **+10** added to your query count. "
            "You can query again, then use **Finish exploration** to retry the same test."
        )
        st.session_state.re_trials_penalty_notice = False

    st.subheader("Exploration")
    st.caption(
        "Edit the input grid, then submit a query. Each successful query increases your query count. "
        "If the verifier errors on your input, the error is shown and that submission is not counted. "
        "The transformation rule is not given in text; infer it from training examples and query outputs."
    )

    if hot_start:
        _render_hot_start_reference(max_px=18)

    st.metric("Queries used", st.session_state.query_count)

    if st.session_state.history:
        st.markdown("---")
        _render_history_section(title="Query history")

    hist_len = len(st.session_state.history)
    max_q = max(1, hist_len)
    if hot_start and st.session_state.hot_start_pair is not None:
        st.markdown("##### Load into editor")
        st.caption(
            "Copy a grid into the query editor below (does not use a query and does not change your count)."
        )
        hc1, hc2, hc3 = st.columns([1, 1, 1])
        with hc1:
            if st.button(
                "Copy free train input",
                key="btn_copy_free_train",
                use_container_width=True,
            ):
                src = st.session_state.hot_start_pair.input
                st.session_state.query_grid = clone_grid(src)
                st.session_state.query_h = len(src)
                st.session_state.query_w = len(src[0]) if src else 1
                _bump_query_editor()
                st.rerun()
        with hc2:
            st.number_input(
                "Query # (copy its input)",
                min_value=1,
                max_value=max_q,
                value=1,
                disabled=hist_len == 0,
                key="hotcopy_query_num",
                help="1 = first query in the history above. Requires at least one completed query.",
            )
        with hc3:
            if st.button(
                "Copy that query's input",
                key="btn_copy_hist_query",
                disabled=hist_len == 0,
                use_container_width=True,
            ):
                n = int(st.session_state.get("hotcopy_query_num", 1))
                i = n - 1
                if 0 <= i < hist_len:
                    src = st.session_state.history[i]["input"]
                    st.session_state.query_grid = clone_grid(src)
                    st.session_state.query_h = len(src)
                    st.session_state.query_w = len(src[0]) if src else 1
                    _bump_query_editor()
                    st.rerun()
                else:
                    st.error("That query number is not in your history.")

    use_arc = arc_grid_editor_available()
    _qnonce = int(st.session_state.get("query_editor_nonce", 0))
    if use_arc:
        st.markdown("**Proposed query input** (arc-app pixel editor — palette + drag to paint)")
        edited_q = arc_grid_editor(
            st.session_state.query_grid,
            key=f"query_arc_grid_{_qnonce}",
        )
        if edited_q is not None:
            st.session_state.query_grid = _normalize_grid_cells(clone_grid(edited_q))
            st.session_state.query_h = len(st.session_state.query_grid)
            st.session_state.query_w = (
                len(st.session_state.query_grid[0]) if st.session_state.query_grid else 1
            )
    else:
        st.info(
            "Pixel editor bundle not found. Run "
            "`npm install` and `npm run build` in "
            "`interface/arc_grid_component/frontend`, then reload. "
            "Using the table fallback below."
        )
        rc1, rc2 = st.columns(2)
        # Key the size inputs with the editor nonce: programmatic grid copies bump
        # the nonce, remounting these widgets so their sticky values cannot revert
        # the just-copied grid's dimensions on the next rerun.
        with rc1:
            qh = st.number_input(
                "Query grid height",
                min_value=1,
                max_value=32,
                value=st.session_state.query_h,
                key=f"qh_in_{_qnonce}",
            )
        with rc2:
            qw = st.number_input(
                "Query grid width",
                min_value=1,
                max_value=32,
                value=st.session_state.query_w,
                key=f"qw_in_{_qnonce}",
            )

        if qh != st.session_state.query_h or qw != st.session_state.query_w:
            st.session_state.query_h = int(qh)
            st.session_state.query_w = int(qw)
            st.session_state.query_grid = _resize_grid(
                st.session_state.query_grid, int(qh), int(qw)
            )
            st.rerun()

        st.markdown("**Proposed query input** (edit cells, integers 0–9)")
        df = _df_from_grid(st.session_state.query_grid)
        edited = st.data_editor(
            df,
            num_rows="fixed",
            hide_index=True,
            use_container_width=True,
            column_config=_arc_column_config(df),
            key=f"query_editor_{_qnonce}",
        )
        st.session_state.query_grid = _grid_from_df(edited)

    b1, b2 = st.columns(2)
    with b1:
        if st.button("Submit query", type="primary", use_container_width=True):
            inp = _normalize_grid_cells(clone_grid(st.session_state.query_grid))
            st.session_state.query_grid = clone_grid(inp)
            try:
                validate_grid(inp)
            except ValueError:
                st.error("Invalid Input Grid or Rule not Applicable")
                st.caption("Fix the grid and try again. This submission was not counted as a query.")
                return

            try:
                gold, used_slot = _run_verifier_chain(inp)
            except RuntimeError:
                st.error("Invalid Input Grid or Rule not Applicable")
                st.caption(
                    "This submission was not counted as a query. "
                    "Adjust the grid or try a different input."
                )
                return

            shown = clone_grid(gold)
            note = ""
            try:
                if noisy_science:
                    shown, corrupted, kind = maybe_corrupt_query_output(
                        task_id,
                        task,
                        used_slot,
                        inp,
                        gold,
                        rng,
                        noise_probability=st.session_state.noise_probability,
                    )
                    note = f"(noisy: {kind})" if corrupted else "(exact)"
                else:
                    note = "(exact)"
            except Exception:
                st.error("Invalid Input Grid or Rule not Applicable")
                st.caption("This submission was not counted as a query.")
                return

            st.session_state.query_count += 1
            st.session_state.history.append(
                {
                    "input": clone_grid(inp),
                    "output": clone_grid(shown),
                    "note": note,
                }
            )
            _default_query_editor_blank()
            st.rerun()

    with b2:
        if st.button("Finish exploration — receive test input", use_container_width=True):
            if not _ensure_test_pair():
                n_prior = len(st.session_state.get("shown_test_inputs") or [])
                if st.session_state.get("hot_start_pair") is not None:
                    n_prior += 1
                st.error(
                    "Could not sample a new dynamic test pair "
                    f"(distinct from {n_prior} prior example(s)). "
                    "Query again or start a new trial."
                )
            else:
                ti = clone_grid(st.session_state.test_pair.input)
                st.session_state.test_h = len(ti)
                st.session_state.test_w = len(ti[0]) if ti else 1
                st.session_state.test_answer_grid = _resize_grid(
                    [[0] * st.session_state.test_w for _ in range(st.session_state.test_h)],
                    st.session_state.test_h,
                    st.session_state.test_w,
                )
                st.session_state.phase = "test"
                _bump_test_editor()
                st.rerun()


def _test_phase() -> None:
    _render_history_section(title="Query history")
    st.subheader("Test")
    st.metric("Query count (score)", st.session_state.query_count)
    tp = st.session_state.test_pair
    if tp is None:
        st.error(
            "Could not sample a dynamic test pair for this task. "
            "Start a new trial, or finish exploration again after another query."
        )
        st.stop()

    if st.session_state.re_trials:
        st.caption(
            "Transform the test input using the rule you inferred. "
            "Submitting this answer does not add queries. "
            "If your answer is wrong, you return to exploration and **+10** is added to your query count. "
            "Use **Copy test input to answer grid** if you want to paint starting from the test pattern."
        )
    else:
        st.caption(
            "Transform the test input using the rule you inferred. This submission does not add queries. "
            "Use **Copy test input to answer grid** to load the test pattern into the answer editor."
        )
    if st.session_state.hot_start:
        _render_hot_start_reference(max_px=18)
        st.markdown("---")
    ti = clone_grid(tp.input)
    _render_grid_ui(ti, title="Test input (read-only)", max_px=22)

    th, tw = len(ti), len(ti[0]) if ti else 1
    st.session_state.test_h = th
    st.session_state.test_w = tw

    if st.button("Copy test input to answer grid", key="btn_copy_test_to_answer", use_container_width=True):
        st.session_state.test_answer_grid = _normalize_grid_cells(clone_grid(ti))
        st.session_state.test_h = th
        st.session_state.test_w = tw
        _bump_test_editor()
        st.rerun()

    # Resize only when not mid-copy; keep programmatic copies intact.
    st.session_state.test_answer_grid = _resize_grid(st.session_state.test_answer_grid, th, tw)

    _tnonce = int(st.session_state.get("test_editor_nonce", 0))
    if arc_grid_editor_available():
        st.markdown("**Your predicted output** (arc-app pixel editor)")
        edited_t = arc_grid_editor(
            st.session_state.test_answer_grid,
            key=f"test_arc_grid_{_tnonce}",
        )
        # Ignore stale returns from a remounted editor right after a programmatic bump.
        if edited_t is not None and not st.session_state.get("_test_editor_force_grid"):
            st.session_state.test_answer_grid = _normalize_grid_cells(clone_grid(edited_t))
        st.session_state._test_editor_force_grid = False
    else:
        st.markdown("**Your predicted output** (table editor)")
        df = _df_from_grid(st.session_state.test_answer_grid)
        edited = st.data_editor(
            df,
            num_rows="fixed",
            hide_index=True,
            use_container_width=True,
            column_config=_arc_column_config(df),
            key=f"test_editor_{_tnonce}",
        )
        if not st.session_state.get("_test_editor_force_grid"):
            st.session_state.test_answer_grid = _grid_from_df(edited)
        st.session_state._test_editor_force_grid = False

    if st.button("Submit final answer", type="primary"):
        pred = _normalize_grid_cells(clone_grid(st.session_state.test_answer_grid))
        st.session_state.test_answer_grid = clone_grid(pred)
        try:
            validate_grid(pred)
        except ValueError:
            st.error("Invalid Input Grid or Rule not Applicable")
            return
        try:
            gold, _slot = _run_verifier_chain(ti)
        except RuntimeError:
            st.error("Invalid Input Grid or Rule not Applicable")
            return
        ok = is_equal_grid(pred, gold)
        if st.session_state.re_trials and not ok:
            st.session_state.query_count += 10
            st.session_state.re_trials_penalty_notice = True
            st.session_state.phase = "explore"
            _default_query_editor_blank()
            st.rerun()

        st.session_state.test_correct = ok
        st.session_state.phase = "done"
        st.rerun()


def _done_phase() -> None:
    _render_history_section(title="Query history")
    st.subheader("Trial complete")
    ok = st.session_state.test_correct
    n = st.session_state.query_count
    st.markdown(f"**Query count:** {n}")
    if ok is None:
        st.warning("No result recorded.")
    else:
        st.markdown("**Final test:** " + ("✅ correct" if ok else "❌ incorrect"))
    st.caption("Lower query counts are better when the final test is correct.")


def main() -> None:
    st.set_page_config(page_title="ActiveARC", layout="wide")
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            min-width: 15rem !important;
            max-width: 15rem !important;
        }
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0.35rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    args = _parse_cli()

    # Migrate older sessions that stored a single `mode` string instead of feature flags.
    if "trial_seed" in st.session_state and "hot_start" not in st.session_state:
        legacy = st.session_state.get("mode", "standard")
        st.session_state.hot_start = legacy == "hot_start"
        st.session_state.noisy_science = legacy == "noisy_science"
        st.session_state.re_trials = legacy == "re_trials"
        st.session_state.pop("mode", None)

    if "trial_seed" not in st.session_state:
        _init_trial(args)

    st.markdown(
        "<h1 style='text-align:center'>ActiveARC</h1>",
        unsafe_allow_html=True,
    )
    _dataset_names = {
        "arc": "ARC-AGI-1",
        "arc2": "ARC-AGI-2",
        "conceptarc": "ConceptARC",
        "parc": "P-ARC",
    }
    _dataset_label = _dataset_names.get(
        st.session_state.get("dataset", "arc"), "ARC-AGI-1"
    )
    st.caption(
        f"Dataset: **{_dataset_label}** · "
        f"Features: **{_mode_caption(st.session_state.hot_start, st.session_state.noisy_science, st.session_state.re_trials)}** "
        f"· trial seed: `{st.session_state.trial_seed}` · "
        f"task: `{st.session_state.task_id}` · validated verifiers available: "
        f"{st.session_state.n_valid_verifiers}"
    )
    if st.session_state.noisy_science:
        st.caption(
            f"Noisy-science corruption probability: **{st.session_state.noise_probability:.2f}** "
            "(each query independently)."
        )
    if st.session_state.re_trials:
        st.caption(
            "**Re-trials:** a wrong final test answer returns you to exploration with **+10** on your query count."
        )

    with st.sidebar:
        st.markdown("### Session")

        _dataset_options = ["arc", "arc2", "conceptarc", "parc"]
        _dataset_labels = {
            "arc": "ARC-AGI-1",
            "arc2": "ARC-AGI-2",
            "conceptarc": "ConceptARC",
            "parc": "P-ARC",
        }
        _current_dataset = st.session_state.get("dataset", args.dataset)
        if _current_dataset not in _dataset_options:
            _current_dataset = "arc"
        _chosen_dataset = st.radio(
            "Dataset",
            _dataset_options,
            index=_dataset_options.index(_current_dataset),
            format_func=lambda d: _dataset_labels[d],
            key="dataset_radio",
            help="ARC-AGI-1 training (400), validated ARC-AGI-2 (200), ConceptARC, or P-ARC (t1–t50).",
        )
        if _chosen_dataset != _current_dataset:
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            _init_trial(
                args,
                seed_override=random.randint(1, 2**31 - 1),
                dataset_override=_chosen_dataset,
                clear_task_id=_chosen_dataset != args.dataset,
            )
            st.rerun()

        if st.session_state.get("dataset") == "arc2":
            _agi2_ids = list(list_agi2_valid_task_ids())
            if _agi2_ids:
                _current_agi2 = st.session_state.get("task_id")
                _agi2_idx = (
                    _agi2_ids.index(_current_agi2)
                    if _current_agi2 in _agi2_ids
                    else 0
                )
                _chosen_agi2 = st.selectbox(
                    "ARC-AGI-2 task",
                    _agi2_ids,
                    index=_agi2_idx,
                    key="arc2_task_select",
                    help="Validated ARC-AGI-2 tasks (same 200-id pool as --dataset arc2).",
                )
                _agi2_ready = st.session_state.get("_arc2_select_ready", False)
                if _agi2_ready and _chosen_agi2 != _current_agi2:
                    for k in list(st.session_state.keys()):
                        del st.session_state[k]
                    _init_trial(
                        args,
                        seed_override=random.randint(1, 2**31 - 1),
                        dataset_override="arc2",
                        task_id_override=_chosen_agi2,
                    )
                    st.rerun()
                st.session_state._arc2_select_ready = True
            else:
                st.warning(
                    "No validated ARC-AGI-2 verifiers found under "
                    "external/agi2_verifiers/valid."
                )

        if st.session_state.get("dataset") == "conceptarc":
            _task_ids = list(list_conceptarc_task_ids())
            _current_task = st.session_state.get("task_id")
            _current_concept = (
                str(_current_task).split("/", 1)[0]
                if _current_task and "/" in str(_current_task)
                else None
            )
            _menu_prev = st.session_state.get("conceptarc_menu_choice")

            if _task_ids:
                if _current_task in _task_ids:
                    _menu_default = _current_task
                elif _menu_prev in _task_ids:
                    _menu_default = _menu_prev
                elif _current_concept:
                    _same = [t for t in _task_ids if t.startswith(_current_concept + "/")]
                    _menu_default = _same[0] if _same else _task_ids[0]
                else:
                    _menu_default = _task_ids[0]

                _chosen_task = st.selectbox(
                    "ConceptARC task",
                    _task_ids,
                    index=_task_ids.index(_menu_default),
                    key="conceptarc_task_select",
                    help="Pick an exported ConceptARC program (official 1–10 or generated 11+).",
                )
                # Only switch when the user actually changes the selectbox value.
                # Do not treat "current trial is a sampled ephemeral id" as a change.
                if _menu_prev is not None and _chosen_task != _menu_prev:
                    for k in list(st.session_state.keys()):
                        del st.session_state[k]
                    _init_trial(
                        args,
                        seed_override=random.randint(1, 2**31 - 1),
                        dataset_override="conceptarc",
                        task_id_override=_chosen_task,
                    )
                    st.session_state.conceptarc_menu_choice = _chosen_task
                    st.rerun()
                st.session_state.conceptarc_menu_choice = _chosen_task
            else:
                _chosen_task = None

            if st.button(
                "Sample new family",
                help=(
                    "Invent a new DSL task family online for the concept of the "
                    "currently selected task (ConceptARC-GEN layer 3)."
                ),
            ):
                _anchor = st.session_state.get("conceptarc_menu_choice") or _chosen_task
                _concept = None
                if _anchor and "/" in str(_anchor):
                    _concept = str(_anchor).split("/", 1)[0]
                elif _current_concept:
                    _concept = _current_concept
                _sample_id = f"{_concept}/sample" if _concept else "sample"
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                _init_trial(
                    args,
                    seed_override=random.randint(1, 2**31 - 1),
                    dataset_override="conceptarc",
                    task_id_override=_sample_id,
                )
                if _anchor:
                    st.session_state.conceptarc_menu_choice = _anchor
                st.rerun()

        if st.session_state.get("dataset") == "parc":
            _parc_ids = list(list_parc_task_ids())
            if _parc_ids:
                _current_parc = st.session_state.get("task_id")
                _parc_idx = (
                    _parc_ids.index(_current_parc)
                    if _current_parc in _parc_ids
                    else 0
                )
                _chosen_parc = st.selectbox(
                    "P-ARC task",
                    _parc_ids,
                    index=_parc_idx,
                    key="parc_task_select",
                    help="P-ARC tasks t1–t50 (ids test2_t1 … test2_t50).",
                )
                _parc_ready = st.session_state.get("_parc_select_ready", False)
                if _parc_ready and _chosen_parc != _current_parc:
                    for k in list(st.session_state.keys()):
                        del st.session_state[k]
                    _init_trial(
                        args,
                        seed_override=random.randint(1, 2**31 - 1),
                        dataset_override="parc",
                        task_id_override=_chosen_parc,
                    )
                    st.rerun()
                st.session_state._parc_select_ready = True
            else:
                st.warning(
                    "P-ARC data not found. Set PARC_ROOT or keep "
                    "PotARCin/PotARCin/Test2 as a sibling checkout."
                )

        if st.button("New trial (same CLI flags)"):
            _keep_dataset = st.session_state.get("dataset", args.dataset)
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            new_seed = random.randint(1, 2**31 - 1)
            _init_trial(
                args,
                seed_override=new_seed,
                dataset_override=_keep_dataset,
                clear_task_id=_keep_dataset != args.dataset,
            )
            st.rerun()
        st.markdown(
            "Use the **Dataset** selector above to switch between ARC-AGI-1, ARC-AGI-2, "
            "ConceptARC, and P-ARC. "
            "Restart the app to change feature flags (`--hot-start`/`--no-hot-start`, `--noisy-science`, "
            "`--re-trials`), `--noise-probability`, `--task-id`, `--dataset`, or `--seed`."
        )

    phase: Phase = st.session_state.phase

    if phase == "explore":
        _explore_phase()
    elif phase == "test":
        _test_phase()
    else:
        _done_phase()


if __name__ == "__main__":
    main()
