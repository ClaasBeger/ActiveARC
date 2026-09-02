"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: a406ac07
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[340](id=340)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0340__a406ac07
"""
from __future__ import annotations



import numpy as np

import copy

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    height = len(grid)
    width = len(grid[0])
    
    # Copy the grid
    output = copy.deepcopy(grid)
    
    # Find horizontal groups in bottom row
    bottom_row = grid[height - 1]
    color_to_horiz = {}
    i = 0
    while i < width:
        c = bottom_row[i]
        if c == 0:
            i += 1
            continue
        start = i
        while i < width and bottom_row[i] == c:
            i += 1
        length = i - start
        color_to_horiz[c] = (start, length)
    
    # Find vertical groups in right column, excluding bottom row
    right_col = [grid[r][width - 1] for r in range(height - 1)]
    vertical_groups = []
    j = 0
    while j < height - 1:
        c = right_col[j]
        if c == 0:
            j += 1
            continue
        start = j
        while j < height - 1 and right_col[j] == c:
            j += 1
        group_height = j - start
        vertical_groups.append((c, start, group_height))
    
    # Apply transformations
    for c, start_r, h in vertical_groups:
        if c in color_to_horiz:
            start_c, len_c = color_to_horiz[c]
            for rr in range(start_r, start_r + h):
                for cc in range(start_c, start_c + len_c):
                    output[rr][cc] = c
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
