"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: f8be4b64
source: GitMonsters/SOLVED-562-verified
original_path: solves/f8be4b64/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__f8be4b64
"""
from __future__ import annotations



"""Solver for ARC-AGI puzzle f8be4b64.

Pattern: Each cross (center surrounded by 3s) extends lines in 4 cardinal
directions using the center color. Lines stop at 3s from other crosses.
Vertical lines take priority over horizontal at intersections.
"""

import json
import copy
from typing import List


def solve(grid: List[List[int]]) -> List[List[int]]:
    rows = len(grid)
    cols = len(grid[0])
    output = copy.deepcopy(grid)

    # Find all crosses: center at (r,c) with 3s at all 4 cardinal neighbors
    crosses = []
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if (grid[r-1][c] == 3 and grid[r+1][c] == 3 and
                    grid[r][c-1] == 3 and grid[r][c+1] == 3):
                crosses.append((r, c, grid[r][c]))

    h_lines = {}  # row -> (set of cols covered, color)
    v_lines = {}  # col -> (set of rows covered, color)

    for r, c, val in crosses:
        # Vertical line extent
        v_rows = {r, r - 1, r + 1}
        for i in range(r - 2, -1, -1):
            if grid[i][c] == 3:
                break
            v_rows.add(i)
        for i in range(r + 2, rows):
            if grid[i][c] == 3:
                break
            v_rows.add(i)
        v_lines[c] = (v_rows, val)

        # Horizontal line extent
        h_cols = {c, c - 1, c + 1}
        for j in range(c - 2, -1, -1):
            if grid[r][j] == 3:
                break
            h_cols.add(j)
        for j in range(c + 2, cols):
            if grid[r][j] == 3:
                break
            h_cols.add(j)
        h_lines[r] = (h_cols, val)

    # Draw horizontal lines first
    for r, (col_set, val) in h_lines.items():
        for j in col_set:
            if grid[r][j] != 3:
                output[r][j] = val

    # Draw vertical lines (overwrite horizontal at intersections)
    for c, (row_set, val) in v_lines.items():
        for i in row_set:
            if grid[i][c] != 3:
                output[i][c] = val

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
