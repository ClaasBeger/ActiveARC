"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: d47aa2ff
source: GitMonsters/SOLVED-562-verified
original_path: solves/d47aa2ff/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__d47aa2ff
"""
from __future__ import annotations



"""
Solver for ARC-AGI task d47aa2ff.

Rule: Input is a 10x21 grid split into left/right 10x10 halves by a column of 5s.
The right half is a near-copy of the left with some cells shifted.
- Where left has a value but right has 0 → mark as 2 (source / moved FROM)
- Where left has 0 but right has a value → mark as 1 (destination / moved TO)
- Otherwise keep the left value.
"""

import json
from typing import List

Grid = List[List[int]]


def solve(grid: Grid) -> Grid:
    rows = len(grid)
    cols = (len(grid[0]) - 1) // 2

    left = [row[:cols] for row in grid]
    right = [row[cols + 1:] for row in grid]

    output = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            l, ri = left[r][c], right[r][c]
            if l != 0 and ri == 0:
                output[r][c] = 2  # source: cell moved away
            elif l == 0 and ri != 0:
                output[r][c] = 1  # destination: cell moved here
            else:
                output[r][c] = l  # unchanged
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
