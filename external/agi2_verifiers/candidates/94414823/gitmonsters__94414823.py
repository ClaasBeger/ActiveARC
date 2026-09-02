"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 94414823
source: GitMonsters/SOLVED-562-verified
original_path: solves/94414823/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__94414823
"""
from __future__ import annotations



"""
Task 94414823: A 5-bordered rectangle with two colored markers outside it.
Fill the 4x4 interior in 2x2 quadrants: each marker's nearest quadrant (and its
diagonal opposite) gets that marker's color.
"""
import json


def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    output = [row[:] for row in grid]

    # Locate the 5-bordered rectangle
    five_cells = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 5]
    min_r = min(r for r, c in five_cells)
    max_r = max(r for r, c in five_cells)
    min_c = min(c for r, c in five_cells)
    max_c = max(c for r, c in five_cells)

    # Interior cell ranges
    ir = list(range(min_r + 1, max_r))
    ic = list(range(min_c + 1, max_c))
    mid_r = (ir[0] + ir[-1]) / 2
    mid_c = (ic[0] + ic[-1]) / 2

    # Find the two colored markers (non-0, non-5)
    markers = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] not in (0, 5):
                markers.append((r, c, grid[r][c]))

    # Map each marker to its nearest quadrant, then fill diagonally opposite too
    quadrant_color: dict[tuple[str, str], int] = {}
    for r, c, color in markers:
        v = "top" if r < mid_r else "bottom"
        h = "left" if c < mid_c else "right"
        quadrant_color[(v, h)] = color

    filled: dict[tuple[str, str], int] = {}
    for (v, h), color in quadrant_color.items():
        filled[(v, h)] = color
        opp_v = "bottom" if v == "top" else "top"
        opp_h = "right" if h == "left" else "left"
        filled[(opp_v, opp_h)] = color

    for r in ir:
        for c in ic:
            v = "top" if r < mid_r else "bottom"
            h = "left" if c < mid_c else "right"
            output[r][c] = filled.get((v, h), 0)

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
