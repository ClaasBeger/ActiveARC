"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ccd554ac
source: GitMonsters/SOLVED-562-verified
original_path: solves/ccd554ac/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__ccd554ac
"""
from __future__ import annotations



def solve(grid):
    n = len(grid)
    m = len(grid[0])
    out = []
    for _ in range(n):
        for row in grid:
            out.append(row * m)
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
