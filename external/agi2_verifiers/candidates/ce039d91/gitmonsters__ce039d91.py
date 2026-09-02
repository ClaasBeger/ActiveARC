"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ce039d91
source: GitMonsters/SOLVED-562-verified
original_path: solves/ce039d91/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__ce039d91
"""
from __future__ import annotations



"""Solver for ARC task ce039d91.

Rule: For each cell with value 5, check the horizontally mirrored position
(col' = width - 1 - col) in the same row. If that position also has a 5,
change this cell to 1. Otherwise keep it as 5.
"""

from typing import List


def solve(grid: List[List[int]]) -> List[List[int]]:
    rows = len(grid)
    cols = len(grid[0])
    result = [row[:] for row in grid]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 5:
                mirror_c = cols - 1 - c
                if grid[r][mirror_c] == 5:
                    result[r][c] = 1
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
