"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ea9794b1
source: GitMonsters/SOLVED-562-verified
original_path: solves/ea9794b1/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__ea9794b1
"""
from __future__ import annotations



"""
ARC-AGI puzzle ea9794b1 solver.

Rule: The 10x10 input is four 5x5 quadrants (TL=4, TR=3, BL=9, BR=8 with 0=empty).
At each position, pick the non-zero value with priority 3 > 9 > 8 > 4.
If all zero, output 0.
"""

import json
from typing import List

PRIORITY = {3: 1, 9: 2, 8: 3, 4: 4}


def solve(grid: List[List[int]]) -> List[List[int]]:
    rows = len(grid) // 2
    cols = len(grid[0]) // 2
    output = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            candidates = [
                grid[r][c],          # TL
                grid[r][c + cols],   # TR
                grid[r + rows][c],   # BL
                grid[r + rows][c + cols],  # BR
            ]
            nonzero = [v for v in candidates if v != 0]
            if nonzero:
                output[r][c] = min(nonzero, key=lambda x: PRIORITY.get(x, 99))
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
