"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 8b28cd80
source: GitMonsters/SOLVED-562-verified
original_path: solves/8b28cd80/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__8b28cd80
"""
from __future__ import annotations



"""
Solver for ARC task 8b28cd80.

Rule: The 3x3 input has exactly one non-zero cell at (r, c) with color value.
Map to a 9x9 source position (sr, sc) = (r*4, c*4).
Each output cell is colored based on Chebyshev distance from the source,
with a spiral seam diagonal that flips the parity.
"""

import json


def solve(grid: list[list[int]]) -> list[list[int]]:
    # Find the non-zero cell
    sr, sc, color = 0, 0, 0
    for r in range(3):
        for c in range(3):
            if grid[r][c] != 0:
                sr, sc, color = r * 4, c * 4, grid[r][c]

    out = [[0] * 9 for _ in range(9)]
    for i in range(9):
        for j in range(9):
            d = max(abs(i - sr), abs(j - sc))
            # Spiral seam: a diagonal line above the source row
            on_seam = (j - i == sc - sr + 1) and (i < sr)
            if on_seam:
                out[i][j] = color if d % 2 == 1 else 0
            else:
                out[i][j] = color if d % 2 == 0 else 0
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
