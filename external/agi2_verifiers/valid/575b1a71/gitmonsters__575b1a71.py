"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 575b1a71
source: GitMonsters/SOLVED-562-verified
original_path: solves/575b1a71/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__575b1a71
"""
from __future__ import annotations



def solve(grid):
    """Replace 0s on background of 5s: each column with 0s gets color 1-4 (left to right)."""
    R, C = len(grid), len(grid[0])
    out = [row[:] for row in grid]

    # Find which columns contain 0s
    cols_with_zeros = sorted({c for r in range(R) for c in range(C) if grid[r][c] == 0})

    # Map columns to colors 1,2,3,4
    col_to_color = {col: i + 1 for i, col in enumerate(cols_with_zeros)}

    for r in range(R):
        for c in range(C):
            if grid[r][c] == 0:
                out[r][c] = col_to_color[c]
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
