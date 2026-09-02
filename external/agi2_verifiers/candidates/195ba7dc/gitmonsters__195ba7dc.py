"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 195ba7dc
source: GitMonsters/SOLVED-562-verified
original_path: solves/195ba7dc/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__195ba7dc
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    # Column 6 is separator (value 2). Left=cols 0-5, Right=cols 7-12.
    result = []
    for r in range(rows):
        row = []
        for c in range(6):
            left = 1 if grid[r][c] == 7 else 0
            right = 1 if grid[r][c + 7] == 7 else 0
            row.append(1 if (left or right) else 0)
        result.append(row)
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
