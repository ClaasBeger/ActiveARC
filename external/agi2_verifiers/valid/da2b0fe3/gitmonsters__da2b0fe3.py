"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: da2b0fe3
source: GitMonsters/SOLVED-562-verified
original_path: solves/da2b0fe3/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__da2b0fe3
"""
from __future__ import annotations



"""Solver for ARC task da2b0fe3.

Rule: The input contains a shape made of two symmetric halves separated by a
single gap row or column (all zeros within the shape's bounding box). The
transformation fills that entire gap row or column across the full grid with 3.
"""

from typing import List


def solve(grid: List[List[int]]) -> List[List[int]]:
    rows = len(grid)
    cols = len(grid[0])
    result = [row[:] for row in grid]

    # Find bounding box of non-zero cells
    min_r, max_r = rows, 0
    min_c, max_c = cols, 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                min_r = min(min_r, r)
                max_r = max(max_r, r)
                min_c = min(min_c, c)
                max_c = max(max_c, c)

    # Check for a horizontal gap (empty row within the bounding box)
    for r in range(min_r, max_r + 1):
        if all(grid[r][c] == 0 for c in range(min_c, max_c + 1)):
            for c in range(cols):
                result[r][c] = 3
            return result

    # Check for a vertical gap (empty column within the bounding box)
    for c in range(min_c, max_c + 1):
        if all(grid[r][c] == 0 for r in range(min_r, max_r + 1)):
            for r in range(rows):
                result[r][c] = 3
            return result

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
