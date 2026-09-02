"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 99306f82
source: GitMonsters/SOLVED-562-verified
original_path: solves/99306f82/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__99306f82
"""
from __future__ import annotations



"""Solver for ARC-AGI task 99306f82.

Pattern: Diagonal pixels at (0,0),(1,1),... give a color sequence.
A rectangle of 1s encloses an empty interior. Fill the interior with
concentric rings of those colors (first diagonal color = outermost ring).
"""
import json
import copy
from typing import List

Grid = List[List[int]]


def solve(grid: Grid) -> Grid:
    out = copy.deepcopy(grid)
    rows, cols = len(grid), len(grid[0])

    # Read diagonal colors until we hit 0 or a 1 (the rectangle border)
    colors = []
    for i in range(min(rows, cols)):
        v = grid[i][i]
        if v == 0 or v == 1:
            break
        colors.append(v)

    # Find the 1-bordered rectangle
    top = left = None
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                top, left = r, c
                break
        if top is not None:
            break

    bot = right = None
    for r in range(rows - 1, -1, -1):
        for c in range(cols - 1, -1, -1):
            if grid[r][c] == 1:
                bot, right = r, c
                break
        if bot is not None:
            break

    # Fill concentric rings inside the rectangle (excluding the 1-border)
    for layer, color in enumerate(colors):
        r1 = top + 1 + layer
        r2 = bot - 1 - layer
        c1 = left + 1 + layer
        c2 = right - 1 - layer
        if r1 > r2 or c1 > c2:
            break
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                out[r][c] = color

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
