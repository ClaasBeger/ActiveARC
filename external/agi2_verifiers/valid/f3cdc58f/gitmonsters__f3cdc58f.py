"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: f3cdc58f
source: GitMonsters/SOLVED-562-verified
original_path: solves/f3cdc58f/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__f3cdc58f
"""
from __future__ import annotations



"""
Solver for ARC task f3cdc58f.

Pattern: Count occurrences of colors 1-4 in the input grid, then build a
bar chart from the bottom-left. Column 0 gets 1s, column 1 gets 2s,
column 2 gets 3s, column 3 gets 4s. Each bar's height equals the count
of that color in the input.
"""

import json
from typing import List


def solve(grid: List[List[int]]) -> List[List[int]]:
    rows = len(grid)
    cols = len(grid[0])
    counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for r in range(rows):
        for c in range(cols):
            v = grid[r][c]
            if v in counts:
                counts[v] += 1

    out = [[0] * cols for _ in range(rows)]
    for color, col_idx in [(1, 0), (2, 1), (3, 2), (4, 3)]:
        h = counts[color]
        for r in range(rows - h, rows):
            out[r][col_idx] = color
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
