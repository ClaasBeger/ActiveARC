"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: a8610ef7
source: GitMonsters/SOLVED-562-verified
original_path: solves/a8610ef7/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__a8610ef7
"""
from __future__ import annotations



def solve(grid):
    # Rule: for each 8-cell, if the vertically flipped cell is also 8 -> 2, else -> 5
    rows, cols = len(grid), len(grid[0])
    result = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 8:
                flipped_r = rows - 1 - r
                if grid[flipped_r][c] == 8:
                    result[r][c] = 2
                else:
                    result[r][c] = 5
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
