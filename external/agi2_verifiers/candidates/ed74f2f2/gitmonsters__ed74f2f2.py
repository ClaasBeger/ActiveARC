"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ed74f2f2
source: GitMonsters/SOLVED-562-verified
original_path: solves/ed74f2f2/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__ed74f2f2
"""
from __future__ import annotations



"""
ARC-AGI puzzle ed74f2f2 solver.

Rule: The 5×9 input contains two 3×3 shapes made of 5s, separated by a column of 0s.
- Left shape (rows 1-3, cols 1-3) determines the output color:
    * Main diagonal (top-left → bottom-right) all filled → color 2
    * Anti-diagonal (top-right → bottom-left) all filled → color 3
    * Neither diagonal fully filled → color 1
- Right shape (rows 1-3, cols 5-7) determines the output pattern.
- Output is the right shape with 5s replaced by the determined color.
"""

import json
from typing import List

Grid = List[List[int]]


def solve(grid: Grid) -> Grid:
    # Extract left and right 3×3 binary shapes
    left = [[1 if grid[r][c] else 0 for c in range(1, 4)] for r in range(1, 4)]
    right = [[1 if grid[r][c] else 0 for c in range(5, 8)] for r in range(1, 4)]

    # Determine color from left shape's diagonal properties
    main_diag = all(left[i][i] for i in range(3))
    anti_diag = all(left[i][2 - i] for i in range(3))

    if main_diag:
        color = 2
    elif anti_diag:
        color = 3
    else:
        color = 1

    return [[color if right[r][c] else 0 for c in range(3)] for r in range(3)]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
