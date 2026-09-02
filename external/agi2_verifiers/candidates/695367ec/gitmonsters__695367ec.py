"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 695367ec
source: GitMonsters/SOLVED-562-verified
original_path: solves/695367ec/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__695367ec
"""
from __future__ import annotations



"""
Solver for ARC task 695367ec.

The input is a uniform NxN grid of a single color C.
The output is a 15x15 grid where grid lines (every N+1 cells) are filled
with color C, and all other cells are 0.
"""

import json
from typing import List


def solve(grid: List[List[int]]) -> List[List[int]]:
    N = len(grid)
    color = grid[0][0]
    step = N + 1  # grid line spacing

    out = [[0] * 15 for _ in range(15)]
    for r in range(15):
        for c in range(15):
            if r % step == N or c % step == N:
                out[r][c] = color
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
