"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: c7d4e6ad
source: GitMonsters/SOLVED-562-verified
original_path: solves/c7d4e6ad/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__c7d4e6ad
"""
from __future__ import annotations



def solve(grid):
    rows = len(grid)
    cols = len(grid[0])
    out = [row[:] for row in grid]
    for r in range(rows):
        color = grid[r][0]
        if color == 0:
            continue
        for c in range(cols):
            if grid[r][c] == 5:
                out[r][c] = color
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
