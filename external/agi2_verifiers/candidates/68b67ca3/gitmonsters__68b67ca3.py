"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 68b67ca3
source: GitMonsters/SOLVED-562-verified
original_path: solves/68b67ca3/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__68b67ca3
"""
from __future__ import annotations



def solve(grid):
    """Scale down by factor 2: each 2x2 block maps to its non-zero value."""
    rows = len(grid)
    cols = len(grid[0])
    out_rows = rows // 2
    out_cols = cols // 2
    out = [[0] * out_cols for _ in range(out_rows)]
    for r in range(out_rows):
        for c in range(out_cols):
            block = [
                grid[2 * r][2 * c], grid[2 * r][2 * c + 1],
                grid[2 * r + 1][2 * c], grid[2 * r + 1][2 * c + 1],
            ]
            for v in block:
                if v != 0:
                    out[r][c] = v
                    break
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
