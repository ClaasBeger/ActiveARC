"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 332efdb3
source: GitMonsters/SOLVED-562-verified
original_path: solves/332efdb3/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__332efdb3
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """output[r][c] = 0 if (r%2==1 and c%2==1) else 1."""
    rows = len(grid)
    cols = len(grid[0])
    return [[0 if (r % 2 == 1 and c % 2 == 1) else 1 for c in range(cols)] for r in range(rows)]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
