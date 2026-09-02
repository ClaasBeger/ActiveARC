"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 31d5ba1a
source: GitMonsters/SOLVED-562-verified
original_path: solves/31d5ba1a/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__31d5ba1a
"""
from __future__ import annotations



"""
Task 31d5ba1a: XOR of two halves.

The input is a 6×5 grid split into two 3×5 halves:
  - Top half uses 9 for "on" and 0 for "off"
  - Bottom half uses 4 for "on" and 0 for "off"

The output is a 3×5 grid where each cell is 6 if exactly one of the
corresponding top/bottom cells is "on" (XOR), and 0 otherwise.
"""
from typing import List


def solve(grid: List[List[int]]) -> List[List[int]]:
    half = len(grid) // 2
    cols = len(grid[0])
    result = []
    for r in range(half):
        row = []
        for c in range(cols):
            top_on = grid[r][c] != 0
            bot_on = grid[r + half][c] != 0
            row.append(6 if top_on ^ bot_on else 0)
        result.append(row)
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
