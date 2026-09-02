"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 66e6c45b
source: GitMonsters/SOLVED-562-verified
original_path: solves/66e6c45b/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__66e6c45b
"""
from __future__ import annotations



def solve(grid):
    """Move center 2x2 values to the four corners of a 4x4 grid."""
    rows = len(grid)
    cols = len(grid[0])
    out = [[0] * cols for _ in range(rows)]
    # Center 2x2 is at rows 1-2, cols 1-2
    out[0][0] = grid[1][1]
    out[0][cols - 1] = grid[1][2]
    out[rows - 1][0] = grid[2][1]
    out[rows - 1][cols - 1] = grid[2][2]
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
