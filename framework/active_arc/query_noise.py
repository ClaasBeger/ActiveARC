from __future__ import annotations

import random
from typing import Literal, Tuple

from framework.corruption.cross_dynamic_mismatch import find_cross_dynamic_mismatch
from framework.corruption.golf_ast import GolfSource, load_and_corrupt_golf_verifier
from framework.corruption.verifier_ast import load_and_corrupt_re_arc_verifier
from framework.dimensions.classification_distribution import VerifierSlot
from framework.grids import (
    Grid,
    GridPair,
    clone_grid,
    is_equal_grid,
    random_color_flips_on_pair,
)
from framework.tasks.base import ArcTask

NoiseKind = Literal["clean", "corrupted_verifier", "color_flip", "instance_mismatch"]


def _corrupt_via_mutated_verifier(
    task_id: str,
    slot: VerifierSlot,
    inp: Grid,
    rng: random.Random,
) -> Grid | None:
    """Wrong output on *inp* using AST-mutated verifier (re_arc or golf)."""
    inp_copy = clone_grid(inp)
    if slot == "re_arc":
        try:
            corrupt_fn, _, _ = load_and_corrupt_re_arc_verifier(
                task_id,
                rng=rng,
                sample_input=inp_copy,
                max_attempts=80,
                max_normalized_cell_edit_distance=0.70,
            )
            return corrupt_fn(clone_grid(inp_copy))
        except Exception:
            return None

    if slot in ("google", "keymoon", "neurips"):
        src: GolfSource = slot  # type: ignore[assignment]
        try:
            corrupt_fn, _, _ = load_and_corrupt_golf_verifier(
                task_id,
                src,
                rng=rng,
                sample_input=inp_copy,
                max_attempts=80,
                max_normalized_cell_edit_distance=0.70,
            )
            return corrupt_fn(clone_grid(inp_copy))
        except Exception:
            return None

    # custom: try re_arc then golf sources
    try:
        corrupt_fn, _, _ = load_and_corrupt_re_arc_verifier(
            task_id,
            rng=rng,
            sample_input=inp_copy,
            max_attempts=80,
            max_normalized_cell_edit_distance=0.70,
        )
        return corrupt_fn(clone_grid(inp_copy))
    except Exception:
        pass
    for src in ("google", "keymoon", "neurips"):
        gs: GolfSource = src  # type: ignore[assignment]
        try:
            corrupt_fn, _, _ = load_and_corrupt_golf_verifier(
                task_id,
                gs,
                rng=rng,
                sample_input=inp_copy,
                max_attempts=80,
                max_normalized_cell_edit_distance=0.70,
            )
            return corrupt_fn(clone_grid(inp_copy))
        except Exception:
            continue
    return None


def _corrupt_via_color_flip(inp: Grid, gold: Grid, rng: random.Random) -> Grid | None:
    pair, _applied = random_color_flips_on_pair(
        GridPair(clone_grid(inp), clone_grid(gold)), rng, max_flips=5
    )
    return clone_grid(pair.output)


def _corrupt_via_instance_mismatch(
    task_id: str, inp: Grid, gold: Grid, rng: random.Random
) -> Grid | None:
    """Borrow another dynamic instance's output for the same task (non-retrieval)."""
    m = find_cross_dynamic_mismatch(
        task_id, GridPair(clone_grid(inp), clone_grid(gold)), pool_size=50
    )
    if m is None:
        return None
    return clone_grid(m.other_instance_pair.output)


def maybe_corrupt_query_output(
    task_id: str,
    task: ArcTask,
    slot: VerifierSlot,
    inp: Grid,
    gold: Grid,
    rng: random.Random,
    *,
    noise_probability: float,
) -> Tuple[Grid, bool, NoiseKind]:
    """With probability *noise_probability*, replace *gold* with a corrupted output.

    Corruption kinds (no retrieval): mutated verifier, color flips, cross-dynamic
    output swap. Falls back to clean output if every attempt matches *gold*.
    """
    p = min(1.0, max(0.0, noise_probability))
    if rng.random() >= p:
        return clone_grid(gold), False, "clean"

    kinds = ["corrupted_verifier", "color_flip", "instance_mismatch"]
    weights = [0.38, 0.34, 0.28]

    for _ in range(14):
        kind = rng.choices(kinds, weights=weights, k=1)[0]
        bad: Grid | None = None
        if kind == "corrupted_verifier":
            bad = _corrupt_via_mutated_verifier(task_id, slot, inp, rng)
        elif kind == "color_flip":
            bad = _corrupt_via_color_flip(inp, gold, rng)
        else:
            bad = _corrupt_via_instance_mismatch(task_id, inp, gold, rng)

        if bad is not None and not is_equal_grid(bad, gold):
            return bad, True, kind  # type: ignore[return-value]

    return clone_grid(gold), False, "clean"
