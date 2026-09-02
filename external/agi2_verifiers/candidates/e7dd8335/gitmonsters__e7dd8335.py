"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e7dd8335
source: GitMonsters/SOLVED-562-verified
original_path: solves/e7dd8335/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__e7dd8335
"""
from __future__ import annotations



def solve(grid):
    """Find the 1-shape, split at vertical midpoint, change bottom half to 2."""
    rows = len(grid)
    cols = len(grid[0])
    out = [row[:] for row in grid]

    # Find row extent of 1s
    one_rows = [r for r in range(rows) for c in range(cols) if grid[r][c] == 1]
    if not one_rows:
        return out

    min_r = min(one_rows)
    max_r = max(one_rows)
    midpoint = (min_r + max_r) / 2.0

    # Change 1s in bottom half to 2
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and r > midpoint:
                out[r][c] = 2

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
