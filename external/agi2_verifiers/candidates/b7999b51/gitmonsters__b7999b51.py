"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: b7999b51
source: GitMonsters/SOLVED-562-verified
original_path: solves/b7999b51/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__b7999b51
"""
from __future__ import annotations



"""Solver for ARC-AGI task b7999b51.

Pattern: Each non-zero color forms a shape. Compute each color's bounding-box
height (number of rows it spans). Output is a "bar chart" — one column per
color, sorted tallest-first, filled from the top with that color.
"""

import json
from typing import List

Grid = List[List[int]]


def solve(grid: Grid) -> Grid:
    # Find row span (bounding-box height) for each color
    color_rows: dict[int, tuple[int, int]] = {}
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val != 0:
                if val not in color_rows:
                    color_rows[val] = (r, r)
                else:
                    lo, hi = color_rows[val]
                    color_rows[val] = (min(lo, r), max(hi, r))

    # height = max_row - min_row + 1
    color_heights = [(hi - lo + 1, color) for color, (lo, hi) in color_rows.items()]
    # Sort descending by height, break ties by color value (arbitrary but consistent)
    color_heights.sort(key=lambda x: (-x[0], x[1]))

    max_h = color_heights[0][0]
    n_cols = len(color_heights)
    out = [[0] * n_cols for _ in range(max_h)]
    for col_idx, (h, color) in enumerate(color_heights):
        for row_idx in range(h):
            out[row_idx][col_idx] = color
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
