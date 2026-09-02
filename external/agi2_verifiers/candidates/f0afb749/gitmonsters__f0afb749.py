"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: f0afb749
source: GitMonsters/SOLVED-562-verified
original_path: solves/f0afb749/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__f0afb749
"""
from __future__ import annotations



"""Solver for ARC-AGI puzzle f0afb749.

Pattern: Each non-zero entry (i,j) in the NxN input defines a circular shift
k = (j - i) % N. For every unique shift k, a full diagonal of 2x2 blocks is
placed in the 2N x 2N output: colored [[v,v],[v,v]] where input is non-zero,
identity [[1,0],[0,1]] where input is zero.
"""

import json
from typing import List

Grid = List[List[int]]


def solve(grid: Grid) -> Grid:
    n = len(grid)
    out = [[0] * (2 * n) for _ in range(2 * n)]

    # Collect unique shifts from non-zero entries
    shifts = set()
    for i in range(n):
        for j in range(n):
            if grid[i][j] != 0:
                shifts.add((j - i) % n)

    # For each shift, lay down a diagonal of 2x2 blocks
    for k in shifts:
        for i in range(n):
            j = (i + k) % n
            r, c = 2 * i, 2 * j
            v = grid[i][j]
            if v != 0:
                out[r][c] = out[r][c + 1] = v
                out[r + 1][c] = out[r + 1][c + 1] = v
            else:
                out[r][c] = 1
                out[r + 1][c + 1] = 1

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
