"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e133d23d
source: GitMonsters/SOLVED-562-verified
original_path: solves/e133d23d/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__e133d23d
"""
from __future__ import annotations



"""
Solver for ARC task e133d23d.

Rule: The input is a 3x7 grid split by a column of 4s (column 3) into
two 3x3 regions. The output is the logical OR of the two regions:
if either region has a non-zero value at a position, output 2; else 0.
"""

import json


def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    out = [[0] * 3 for _ in range(rows)]
    for r in range(rows):
        for c in range(3):
            left = grid[r][c]
            right = grid[r][c + 4]
            out[r][c] = 2 if (left != 0 or right != 0) else 0
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
