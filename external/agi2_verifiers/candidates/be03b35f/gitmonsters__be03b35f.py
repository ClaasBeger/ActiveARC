"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: be03b35f
source: GitMonsters/SOLVED-562-verified
original_path: solves/be03b35f/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__be03b35f
"""
from __future__ import annotations



"""
ARC-AGI solver for task be03b35f.

The 5×5 input grid is divided into four 2×2 quadrants by a cross of zeros
at row 2 and column 2. The bottom-right quadrant is all 2s (the "canvas").
The output is the top-left quadrant rotated 90° counter-clockwise.
"""
import json


def solve(grid: list[list[int]]) -> list[list[int]]:
    # Extract top-left 2×2 quadrant
    a, b = grid[0][0], grid[0][1]
    c, d = grid[1][0], grid[1][1]
    # Rotate 90° CCW: [[a,b],[c,d]] → [[b,d],[a,c]]
    return [[b, d], [a, c]]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
