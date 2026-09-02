"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 0becf7df
source: GitMonsters/SOLVED-562-verified
original_path: solves/0becf7df/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__0becf7df
"""
from __future__ import annotations



import json, sys

def solve(grid):
    rows = len(grid)
    cols = len(grid[0])
    result = [row[:] for row in grid]

    # 2x2 key: same-row elements swap
    mapping = {
        grid[0][0]: grid[0][1],
        grid[0][1]: grid[0][0],
        grid[1][0]: grid[1][1],
        grid[1][1]: grid[1][0],
    }

    for r in range(rows):
        for c in range(cols):
            if r < 2 and c < 2:
                continue
            if grid[r][c] != 0 and grid[r][c] in mapping:
                result[r][c] = mapping[grid[r][c]]

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
