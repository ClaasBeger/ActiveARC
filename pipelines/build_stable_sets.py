#!/usr/bin/env python3
"""Freeze a fixed stable evaluation set per task by sampling its generator.

Draws distinct generator pairs until ``--n`` are collected (250 by default) and
writes them to ``experiments/stable_sets/<dataset>/<task_id>.json``. Programs are
then scored against the same fixed examples on every run, instead of a fresh
dynamic draw::

    python -m pipelines.build_stable_sets --dataset arc --limit 400
    python -m pipelines.build_stable_sets --from-run experiments/runs/prog_parc50_astra_seed0

Pairs are kept only if the task's own verifier reproduces them, so the frozen set
agrees with the oracle the model queried during the trial.
"""

from __future__ import annotations

import argparse
import copy
import gzip
import json
import random
import signal
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from framework.grids import GridPair, is_equal_grid
from framework.tasks.base import ArcTask, Verifier

DEFAULT_OUT_DIR = ROOT_DIR / "experiments" / "stable_sets"
DEFAULT_N = 250
SKIP_FILES = {"manifest.json", "summary.json", "program_scores.json"}


def safe_name(task_id: str) -> str:
    """Filesystem-safe task id (ConceptARC ids contain ``/``)."""
    return task_id.replace("/", "__")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Freeze per-task stable evaluation sets")
    p.add_argument(
        "--dataset",
        choices=["arc", "arc2", "conceptarc", "parc"],
        default=None,
        help="Build for a whole dataset (ignored when --from-run is given).",
    )
    p.add_argument(
        "--from-run",
        type=str,
        default=None,
        help="Take the task list (and dataset) from an existing run directory.",
    )
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--per-concept-limit", type=int, default=None)
    p.add_argument("--task-id", type=str, default=None, help="Single task id.")
    p.add_argument("--n", type=int, default=DEFAULT_N, help=f"Pairs per task (default {DEFAULT_N}).")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument(
        "--batch",
        type=int,
        default=300,
        help="Generator draw size per attempt (default 300).",
    )
    p.add_argument(
        "--max-attempts",
        type=int,
        default=6,
        help="Generator batches to draw before giving up on reaching --n.",
    )
    p.add_argument(
        "--task-timeout-s",
        type=float,
        default=30.0,
        help="Hard per-task wall-clock cap: interrupts the generator mid-call and "
        "keeps whatever was collected (0 = no cap). Healthy tasks finish in well "
        "under a second, so 30s only ever trims hung or pathologically slow "
        "generators. Worst case total = this x number of tasks.",
    )
    p.add_argument(
        "--verify",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Keep only pairs the task verifier reproduces (default: true).",
    )
    p.add_argument("--out-dir", type=str, default=str(DEFAULT_OUT_DIR))
    p.add_argument(
        "--gzip",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Write .json.gz (grids compress ~20x). Default: true.",
    )
    p.add_argument("--skip-existing", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument(
        "--improve-short",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Retry only tasks whose stored set is below --n, keeping whichever "
        "result has more pairs. Sets already marked exhausted are left alone.",
    )
    return p.parse_args()


def _load_task(dataset: str, task_id: str) -> ArcTask:
    if dataset == "parc":
        from framework.tasks.parc_dataset import load_parc_task

        return load_parc_task(task_id)
    if dataset == "conceptarc":
        from framework.integrations.conceptarc_adapter import load_conceptarc_task

        return load_conceptarc_task(task_id)
    from framework.tasks.arc_dataset import load_task

    return load_task(task_id, load_alternative_verifiers=False)


def _task_verifier(dataset: str, task: ArcTask) -> Optional[Verifier]:
    """The oracle a trial would use: pinned re_arc-preferred slot, else the task's own."""
    if dataset in ("parc", "conceptarc"):
        return task.quinary_verifier or task.verifier
    from framework.active_arc.verifier_selection import list_valid_verifiers

    valid = list_valid_verifiers(task)
    if valid:
        return valid[0][1]
    return task.verifier


def _task_ids(args: argparse.Namespace) -> Tuple[str, List[str]]:
    if args.from_run:
        run = Path(args.from_run)
        manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
        return manifest.get("dataset", "arc"), list(manifest.get("task_ids") or [])
    dataset = args.dataset or "arc"
    if args.task_id:
        return dataset, [args.task_id]
    if dataset == "arc":
        from framework.tasks.arc_dataset import list_arc_agi_1_task_ids

        ids = list(list_arc_agi_1_task_ids())
    elif dataset == "arc2":
        from framework.integrations.agi2_verifiers import list_agi2_valid_task_ids

        ids = list(list_agi2_valid_task_ids())
    elif dataset == "conceptarc":
        from framework.integrations.conceptarc_adapter import list_conceptarc_task_ids

        ids = list(list_conceptarc_task_ids())
        if args.per_concept_limit is not None:
            by_concept: Dict[str, List[str]] = {}
            for tid in ids:
                by_concept.setdefault(tid.split("/", 1)[0], []).append(tid)
            ids = [t for c in sorted(by_concept) for t in sorted(by_concept[c])[: args.per_concept_limit]]
    else:
        from framework.tasks.parc_dataset import list_parc_task_ids

        ids = list(list_parc_task_ids())
    if args.limit is not None:
        ids = ids[args.offset : args.offset + args.limit]
    return dataset, ids


@contextmanager
def _time_limit(seconds: float):
    """Interrupt a generator call that runs too long (main thread only)."""
    if seconds <= 0 or not hasattr(signal, "SIGALRM"):
        yield
        return

    def _raise(_sig, _frm):
        raise TimeoutError(f"generator call exceeded {seconds}s")

    try:
        previous = signal.signal(signal.SIGALRM, _raise)
    except ValueError:
        yield
        return
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, previous)


def _draw(task: ArcTask, n: int, rng: random.Random, timeout_s: float = 0.0) -> List[GridPair]:
    """Draw *n* generator pairs, bounded by *timeout_s* (a hung generator yields [])."""
    gen = task.arc_gen_generator
    if gen is None:
        return []
    try:
        with _time_limit(timeout_s):
            return list(gen(n, rng))
    except TypeError:
        pass
    except Exception:
        return []
    try:
        with _time_limit(timeout_s):
            return list(gen(n))
    except Exception:
        return []


def _draw_singles(
    task: ArcTask,
    n: int,
    rng: random.Random,
    *,
    deadline: float,
    per_call_timeout_s: float = 2.0,
) -> List[GridPair]:
    """Draw pairs one at a time, skipping calls that raise or hang.

    Several ARC-GEN V2 generators fail or loop when asked for a large batch but
    are perfectly healthy one pair at a time, so a single bad draw must not take
    the whole batch down with it.
    """
    gen = task.arc_gen_generator
    if gen is None:
        return []
    out: List[GridPair] = []
    misses = 0
    while len(out) < n and time.perf_counter() < deadline and misses < 200:
        try:
            with _time_limit(per_call_timeout_s):
                try:
                    drawn = list(gen(1, rng))
                except TypeError:
                    drawn = list(gen(1))
        except Exception:
            misses += 1
            continue
        if drawn:
            out.extend(drawn)
        else:
            misses += 1
    return out


def build_stable_set(
    dataset: str,
    task_id: str,
    *,
    n: int,
    seed: int,
    batch: int,
    max_attempts: int,
    verify: bool,
    task_timeout_s: float = 0.0,
) -> Dict[str, Any]:
    """Collect up to *n* distinct verified generator pairs for one task."""
    task = _load_task(dataset, task_id)
    verifier = _task_verifier(dataset, task) if verify else None
    rng = random.Random(seed)
    pairs: List[GridPair] = []
    seen: set = set()
    n_rejected = 0
    # Start from any committed pool (ARC-GEN stable, or P-ARC's 50) and top up.
    n_seeded = 0
    for pair in list(task.arc_gen_synthetic_pairs or []) + list(task.p_arc_stable_pairs or []):
        key = json.dumps(pair.input)
        if key in seen or len(pairs) >= n:
            continue
        if verifier is not None:
            try:
                if not is_equal_grid(verifier(copy.deepcopy(pair.input)), pair.output):
                    n_rejected += 1
                    continue
            except Exception:
                n_rejected += 1
                continue
        seen.add(key)
        pairs.append(pair)
        n_seeded += 1
    attempts = 0
    started = time.perf_counter()
    timed_out = False
    used_singles = False
    exhausted = False
    while len(pairs) < n and attempts < max_attempts:
        if task_timeout_s and time.perf_counter() - started > task_timeout_s:
            timed_out = True
            break
        attempts += 1
        before = len(pairs)
        remaining = (task_timeout_s - (time.perf_counter() - started)) if task_timeout_s else 0.0
        # Give the batch call only a slice of the budget: when it hangs, the
        # per-pair fallback below still has time to work.
        batch_timeout = min(max(remaining, 1.0), 5.0) if task_timeout_s else 0.0
        drawn = _draw(task, batch, rng, timeout_s=batch_timeout)
        if not drawn:
            # Batch call failed or hung: fall back to one-at-a-time drawing, which
            # many ARC-GEN V2 generators tolerate even when a batch call does not.
            deadline = (started + task_timeout_s) if task_timeout_s else (time.perf_counter() + 60.0)
            drawn = _draw_singles(task, n - len(pairs), rng, deadline=deadline)
            used_singles = True
            if not drawn:
                break
        for pair in drawn:
            key = json.dumps(pair.input)
            if key in seen:
                continue
            if verifier is not None:
                try:
                    if not is_equal_grid(verifier(copy.deepcopy(pair.input)), pair.output):
                        n_rejected += 1
                        continue
                except Exception:
                    n_rejected += 1
                    continue
            seen.add(key)
            pairs.append(pair)
            if len(pairs) >= n:
                break
        if len(pairs) == before:
            # A whole round produced no new distinct input: the generator's input
            # space is exhausted, so more time would not help.
            exhausted = True
            break
    return {
        "task_id": task_id,
        "dataset": dataset,
        "requested": n,
        "n": len(pairs),
        "seed": seed,
        "verified": verify,
        "n_rejected": n_rejected,
        "n_seeded_from_pool": n_seeded,
        "attempts": attempts,
        "timed_out": timed_out,
        "used_singles": used_singles,
        "exhausted": exhausted,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pairs": [{"input": p.input, "output": p.output} for p in pairs],
    }


def main() -> None:
    args = _parse_args()
    dataset, ids = _task_ids(args)
    if not ids:
        raise SystemExit("No task ids selected.")
    out_dir = Path(args.out_dir) / dataset
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    short: List[Tuple[str, int]] = []
    failed: List[Tuple[str, str]] = []
    for i, task_id in enumerate(ids, 1):
        suffix = ".json.gz" if args.gzip else ".json"
        path = out_dir / f"{safe_name(task_id)}{suffix}"
        previous: Optional[Dict[str, Any]] = None
        if args.improve_short and path.is_file():
            try:
                opener = gzip.open if args.gzip else open
                with opener(path, "rt", encoding="utf-8") as f:  # type: ignore[operator]
                    previous = json.load(f)
            except Exception:
                previous = None
            if previous is not None and (
                previous.get("n", 0) >= args.n or previous.get("exhausted")
            ):
                state = "exhausted" if previous.get("exhausted") else "already full"
                print(f"[{i}/{len(ids)}] skip {task_id} ({state}, {previous.get('n')} pairs)", flush=True)
                continue
        elif args.skip_existing and path.is_file():
            print(f"[{i}/{len(ids)}] skip existing {task_id}", flush=True)
            continue
        started = time.perf_counter()
        try:
            payload = build_stable_set(
                dataset,
                task_id,
                n=args.n,
                seed=args.seed,
                batch=args.batch,
                max_attempts=args.max_attempts,
                verify=args.verify,
                task_timeout_s=args.task_timeout_s,
            )
        except Exception as e:
            failed.append((task_id, f"{type(e).__name__}: {e}"))
            print(f"[{i}/{len(ids)}] {task_id}: FAILED {type(e).__name__}: {e}", flush=True)
            continue
        if previous is not None and previous.get("n", 0) >= payload["n"]:
            print(
                f"[{i}/{len(ids)}] {task_id}: kept previous {previous['n']} pairs "
                f"(retry got {payload['n']})",
                flush=True,
            )
            continue
        blob = json.dumps(payload, separators=(",", ":"))
        if args.gzip:
            with gzip.open(path, "wt", encoding="utf-8") as f:
                f.write(blob)
        else:
            path.write_text(blob, encoding="utf-8")
        if payload["n"] < args.n:
            short.append((task_id, payload["n"]))
        print(
            f"[{i}/{len(ids)}] {task_id}: {payload['n']}/{args.n} pairs "
            f"(pool {payload['n_seeded_from_pool']}) "
            f"(rejected {payload['n_rejected']}, {time.perf_counter() - started:.1f}s"
            + (", TIMED OUT)" if payload.get("timed_out") else ")"),
            flush=True,
        )

    print(
        f"\ndone in {(time.perf_counter() - t0) / 60:.1f} min · short of {args.n}: {len(short)} · failed: {len(failed)}",
        flush=True,
    )
    for tid, got in short[:20]:
        print(f"  short: {tid} -> {got}", flush=True)
    for tid, err in failed[:20]:
        print(f"  failed: {tid} -> {err}", flush=True)


if __name__ == "__main__":
    main()
