"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 705a3229
source: GitMonsters/SOLVED-562-verified
original_path: solves/705a3229/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__705a3229
"""
from __future__ import annotations



"""
ARC-AGI Puzzle 705a3229 Solver

Rule: Each non-zero pixel draws an L-shape toward its nearest grid corner
(by Manhattan distance). One arm extends along the row to the corner's
column edge, the other along the column to the corner's row edge.
"""

import json
import copy
from typing import List

Grid = List[List[int]]

TASK_PATH = "/Users/evanpieser/ARC_AMD_TRANSFER/data/ARC-AGI/data/evaluation/705a3229.json"


def solve(grid: Grid) -> Grid:
    rows, cols = len(grid), len(grid[0])
    out = copy.deepcopy(grid)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                continue
            val = grid[r][c]

            corners = [
                (0, 0),            # top-left
                (0, cols - 1),     # top-right
                (rows - 1, 0),    # bottom-left
                (rows - 1, cols - 1),  # bottom-right
            ]
            # Nearest corner by Manhattan distance
            cr, cc = min(corners, key=lambda corner: abs(corner[0] - r) + abs(corner[1] - c))

            # Vertical arm toward corner row
            step = 1 if cr >= r else -1
            for rr in range(r, cr + step, step):
                out[rr][c] = val

            # Horizontal arm toward corner col
            step = 1 if cc >= c else -1
            for cc2 in range(c, cc + step, step):
                out[r][cc2] = val

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
