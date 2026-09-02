"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 712bf12e
source: GitMonsters/SOLVED-562-verified
original_path: solves/712bf12e/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__712bf12e
"""
from __future__ import annotations



"""
ARC-AGI Puzzle 712bf12e Solver

Rule: Each 2 in the bottom row emits a vertical line upward. When the line
hits a 5, it shifts one column to the right (placing a corner piece in the
row below at the new column). If the corner position contains a 5 or is out
of bounds, the line terminates. Multiple consecutive 5s cause multiple shifts.
"""

import json
import copy
import sys


def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    output = copy.deepcopy(grid)

    bottom_row = rows - 1
    starts = [c for c in range(cols) if grid[bottom_row][c] == 2]

    for start_col in starts:
        col = start_col
        for row in range(bottom_row - 1, -1, -1):
            placed = False
            while col < cols:
                if grid[row][col] == 5:
                    # Shift right: place corner one row below at col+1
                    new_col = col + 1
                    if new_col >= cols:
                        break
                    if grid[row + 1][new_col] == 5:
                        break
                    output[row + 1][new_col] = 2
                    col = new_col
                else:
                    output[row][col] = 2
                    placed = True
                    break
            if not placed:
                break

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
