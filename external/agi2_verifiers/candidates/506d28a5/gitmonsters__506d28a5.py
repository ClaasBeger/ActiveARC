"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 506d28a5
source: GitMonsters/SOLVED-562-verified
original_path: solves/506d28a5/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__506d28a5
"""
from __future__ import annotations



def solve(grid):
    """OR two halves split by a row of 4s: non-zero in either half → 3."""
    R, C = len(grid), len(grid[0])
    # Find the separator row (all 4s)
    sep = None
    for r in range(R):
        if all(v == 4 for v in grid[r]):
            sep = r
            break
    top = grid[:sep]
    bot = grid[sep + 1:]
    out = []
    for r in range(len(top)):
        row = []
        for c in range(C):
            if top[r][c] != 0 or bot[r][c] != 0:
                row.append(3)
            else:
                row.append(0)
        out.append(row)
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
