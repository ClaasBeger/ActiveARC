"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 2072aba6
source: GitMonsters/SOLVED-562-verified
original_path: solves/2072aba6/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__2072aba6
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """Each 5-cell maps to 2x2 block [[1,2],[2,1]]. Zero cells map to 2x2 zeros."""
    r = len(grid)
    c = len(grid[0])
    out = [[0]*(c*2) for _ in range(r*2)]

    for i in range(r):
        for j in range(c):
            if grid[i][j] == 5:
                out[i*2][j*2] = 1
                out[i*2][j*2+1] = 2
                out[i*2+1][j*2] = 2
                out[i*2+1][j*2+1] = 1

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
