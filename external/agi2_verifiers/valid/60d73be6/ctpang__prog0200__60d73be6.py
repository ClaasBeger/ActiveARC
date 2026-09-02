"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 60d73be6
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[200](id=200)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0200__60d73be6
"""
from __future__ import annotations



import numpy as np

import copy

def transform(grid: list[list[int]]) -> list[list[int]]:
    out = copy.deepcopy(grid)
    rows = len(grid)
    if rows == 0:
        return out
    cols = len(grid[0])

    # Find horizontal_row
    horizontal_row = -1
    C = -1
    for r in range(rows):
        first = grid[r][0]
        if all(grid[r][c] == first for c in range(cols)) and first != 7 and first != 0:
            horizontal_row = r
            C = first
            break

    if horizontal_row == -1:
        return out

    # Find vertical_col
    vertical_col = -1
    for cc in range(cols):
        first = grid[0][cc]
        if all(grid[r][cc] == first for r in range(rows)) and first == C:
            vertical_col = cc
            break

    if vertical_col == -1:
        return out

    # Symmetrize vertical (left-right)
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 7 and grid[r][c] != C:
                c_mirror = 2 * vertical_col - c
                if 0 <= c_mirror < cols:
                    out[r][c_mirror] = grid[r][c]

    # Now, symmetrize horizontal (up-down) on the updated out
    grid2 = copy.deepcopy(out)
    for r in range(rows):
        for c in range(cols):
            if out[r][c] != 7 and out[r][c] != C:
                r_mirror = 2 * horizontal_row - r
                if 0 <= r_mirror < rows:
                    grid2[r_mirror][c] = out[r][c]

    return grid2

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
