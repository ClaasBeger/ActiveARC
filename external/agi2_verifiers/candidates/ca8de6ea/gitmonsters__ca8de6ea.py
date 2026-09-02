"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ca8de6ea
source: GitMonsters/SOLVED-562-verified
original_path: solves/ca8de6ea/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__ca8de6ea
"""
from __future__ import annotations



"""
ARC-AGI solver for task ca8de6ea.

The 5×5 input has non-zero values on its two diagonals forming an X shape
(9 unique cells). The output is a 3×3 grid that compresses the X by mapping:
  - Outer corners → output corners
  - Inner diagonal cells → output edges
  - Center → output center
"""
import json


def solve(grid: list[list[int]]) -> list[list[int]]:
    return [
        [grid[0][0], grid[1][1], grid[0][4]],
        [grid[3][1], grid[2][2], grid[1][3]],
        [grid[4][0], grid[3][3], grid[4][4]],
    ]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
