"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e633a9e5
source: GitMonsters/SOLVED-562-verified
original_path: solves/e633a9e5/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__e633a9e5
"""
from __future__ import annotations



"""
Solver for ARC task e633a9e5.

Transformation: 3x3 → 5x5 non-uniform scaling.
  - Rows 0 and 2 are doubled in height; row 1 stays single.
  - Columns 0 and 2 are doubled in width; column 1 stays single.
"""

import json
from typing import List


def solve(grid: List[List[int]]) -> List[List[int]]:
    row_map = [0, 0, 1, 2, 2]
    col_map = [0, 0, 1, 2, 2]
    return [[grid[row_map[r]][col_map[c]] for c in range(5)] for r in range(5)]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
