"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 8e2edd66
source: GitMonsters/SOLVED-562-verified
original_path: solves/8e2edd66/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__8e2edd66
"""
from __future__ import annotations



"""
Solver for ARC task 8e2edd66.

Transformation: 3x3 → 9x9 tiled grid.
For each cell in the 3x3 input:
  - If the cell is 0: place the "inverted" input (0↔color swapped) in that 3x3 block.
  - If the cell is non-zero: place all zeros in that 3x3 block.
"""

import json
from typing import List


def solve(grid: List[List[int]]) -> List[List[int]]:
    color = next(v for row in grid for v in row if v != 0)
    inverted = [[color if v == 0 else 0 for v in row] for row in grid]
    output = [[0] * 9 for _ in range(9)]
    for br in range(3):
        for bc in range(3):
            if grid[br][bc] == 0:
                for r in range(3):
                    for c in range(3):
                        output[br * 3 + r][bc * 3 + c] = inverted[r][c]
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
