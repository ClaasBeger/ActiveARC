"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 37ce87bb
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[108](id=108)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0108__37ce87bb
"""
from __future__ import annotations



import numpy as np

import copy

def transform(grid: list[list[int]]) -> list[list[int]]:
    new_grid = copy.deepcopy(grid)
    rows = len(grid)
    cols = len(grid[0])
    purple_sum = 0
    red_sum = 0
    max_j = -1
    for j in range(cols):
        if grid[rows - 1][j] == 7:
            continue
        color = grid[rows - 1][j]
        if color not in (2, 8):
            continue
        h = 1
        for r in range(rows - 2, -1, -1):
            if grid[r][j] == color:
                h += 1
            else:
                break
        if color == 8:
            purple_sum += h
        elif color == 2:
            red_sum += h
        max_j = max(max_j, j)
    grey_h = purple_sum - red_sum
    if grey_h <= 0 or max_j == -1:
        return new_grid
    new_j = max_j + 2
    if new_j >= cols:
        return new_grid
    for i in range(grey_h):
        r = rows - 1 - i
        new_grid[r][new_j] = 5
    return new_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
