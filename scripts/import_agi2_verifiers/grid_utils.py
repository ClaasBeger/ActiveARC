"""Grid helpers for verifier import (stdlib-only for worker processes)."""

from __future__ import annotations

import copy
from typing import Any, List, Optional, Sequence, Tuple

Grid = List[List[int]]


def to_grid(value: Any) -> Optional[Grid]:
    """Normalize numpy / nested sequences to a rectangular list[list[int]], or None."""
    if value is None:
        return None
    if hasattr(value, "tolist"):
        try:
            value = value.tolist()
        except Exception:
            return None
    if not isinstance(value, (list, tuple)) or not value:
        return None
    rows: Grid = []
    width: Optional[int] = None
    for row in value:
        if hasattr(row, "tolist"):
            try:
                row = row.tolist()
            except Exception:
                return None
        if not isinstance(row, (list, tuple)) or not row:
            return None
        cells: List[int] = []
        for cell in row:
            try:
                if hasattr(cell, "item"):
                    cell = cell.item()
                cells.append(int(cell))
            except Exception:
                return None
        if width is None:
            width = len(cells)
        elif len(cells) != width:
            return None
        rows.append(cells)
    return rows


def grids_equal(a: Any, b: Any) -> bool:
    ga = to_grid(a)
    gb = to_grid(b)
    if ga is None or gb is None:
        return False
    if len(ga) != len(gb):
        return False
    return all(ra == rb for ra, rb in zip(ga, gb))


def deep_copy_grid(grid: Grid) -> Grid:
    return copy.deepcopy(grid)


def load_official_pairs(task_json: dict) -> List[Tuple[str, int, Grid, Grid]]:
    """Return (split, index, input, output) for every official train/test pair."""
    out: List[Tuple[str, int, Grid, Grid]] = []
    for split in ("train", "test"):
        for i, pair in enumerate(task_json.get(split) or []):
            inp = to_grid(pair.get("input"))
            exp = to_grid(pair.get("output"))
            if inp is None or exp is None:
                raise ValueError(f"malformed official pair {split}[{i}]")
            out.append((split, i, inp, exp))
    if not out:
        raise ValueError("task has no official pairs")
    return out


def passes_official(fn, pairs: Sequence[Tuple[str, int, Grid, Grid]]) -> Tuple[bool, Optional[str]]:
    """Return (ok, failure_detail). Used for CT Pang alignment (in-process)."""
    for split, i, inp, exp in pairs:
        before = deep_copy_grid(inp)
        try:
            got = fn(deep_copy_grid(inp))
        except Exception as e:
            return False, f"{split}[{i}] exception: {type(e).__name__}: {e}"
        if before != inp:
            # input arg was not the same object; check mutation of the working copy only via got
            pass
        if not grids_equal(got, exp):
            return False, f"{split}[{i}] incorrect_output"
    return True, None
