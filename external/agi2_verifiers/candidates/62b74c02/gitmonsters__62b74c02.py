"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 62b74c02
source: GitMonsters/SOLVED-562-verified
original_path: solves/62b74c02/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__62b74c02
"""
from __future__ import annotations



def solve(grid):
    """Left pattern + fill with border color + duplicate left pattern on right."""
    R, C = len(grid), len(grid[0])
    # Find pattern width: first zero in first row
    pw = C
    for c in range(C):
        if grid[0][c] == 0:
            pw = c
            break
    out = []
    for r in range(R):
        left = grid[r][:pw]
        border = left[0]
        fill_len = C - 2 * pw
        out.append(left + [border] * fill_len + left)
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
