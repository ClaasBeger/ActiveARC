"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: c658a4bd
source: GitMonsters/SOLVED-562-verified
original_path: solves/c658a4bd/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__c658a4bd
"""
from __future__ import annotations



"""Solver for ARC-AGI task c658a4bd.

Pattern: The input contains several colored hollow rectangles scattered
(and partially overlapping) on a black background. The output nests them
concentrically, ordered by bounding-box size (largest = outermost layer,
smallest = innermost fill).
"""

from typing import List

Grid = List[List[int]]


def solve(grid: Grid) -> Grid:
    rows, cols = len(grid), len(grid[0])

    # Find bounding box for every non-zero color
    color_bounds: dict[int, list[int]] = {}
    for r in range(rows):
        for c in range(cols):
            v = grid[r][c]
            if v == 0:
                continue
            if v not in color_bounds:
                color_bounds[v] = [r, r, c, c]
            else:
                b = color_bounds[v]
                if r < b[0]: b[0] = r
                if r > b[1]: b[1] = r
                if c < b[2]: b[2] = c
                if c > b[3]: b[3] = c

    # Size = max(height, width) of each bounding box; sort descending
    layers = sorted(
        ((max(b[1] - b[0] + 1, b[3] - b[2] + 1), color)
         for color, b in color_bounds.items()),
        reverse=True,
    )

    n = layers[0][0]  # output side length = size of largest rectangle
    output = [[0] * n for _ in range(n)]

    # Paint from outermost to innermost (each overwrites the center)
    for i, (_size, color) in enumerate(layers):
        for r in range(i, n - i):
            for c in range(i, n - i):
                output[r][c] = color

    return output


# --------------- verification ---------------

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
