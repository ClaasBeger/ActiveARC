"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 137f0df0
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[30](id=30)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0030__137f0df0
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = [row[:] for row in grid]
    rows = len(grid)
    cols = len(grid[0])
    
    # Find min_col and max_col
    min_col = cols
    max_col = -1
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 5:
                min_col = min(min_col, j)
                max_col = max(max_col, j)
    if max_col < 0:
        return grid
    
    left_ext = min_col
    right_ext = cols - 1 - max_col
    
    arm_cols = set()
    is_grey = [False] * rows
    for r in range(rows):
        has_grey = any(grid[r][j] == 5 for j in range(cols))
        is_grey[r] = has_grey
        if has_grey:
            for j in range(min_col, max_col + 1):
                if grid[r][j] == 0:
                    grid[r][j] = 2
                    arm_cols.add(j)
    
    # Fill empty bands
    r = 0
    while r < rows:
        if is_grey[r]:
            while r < rows and is_grey[r]:
                r += 1
            continue
        empty_start = r
        while r < rows and not is_grey[r]:
            r += 1
        h = r - empty_start
        is_top = (empty_start == 0)
        is_bottom = (r == rows)
        is_internal = not (is_top or is_bottom)
        if is_internal:
            for rr in range(empty_start, empty_start + h):
                for j in range(left_ext):
                    grid[rr][j] = 1
                for j in range(min_col, max_col + 1):
                    grid[rr][j] = 2
                for j in range(max_col + 1, max_col + 1 + right_ext):
                    grid[rr][j] = 1
        else:
            for rr in range(empty_start, empty_start + h):
                for j in arm_cols:
                    grid[rr][j] = 1
    
    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
