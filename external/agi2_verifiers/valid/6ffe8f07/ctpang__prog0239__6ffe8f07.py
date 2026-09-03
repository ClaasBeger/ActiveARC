"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 6ffe8f07
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[239](id=239)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0239__6ffe8f07
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    output = [row[:] for row in grid]

    # Find purple bounds
    min_r, max_r, min_c, max_c = rows, -1, cols, -1
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 8:
                min_r = min(min_r, r)
                max_r = max(max_r, r)
                min_c = min(min_c, c)
                max_c = max(max_c, c)

    if min_r > max_r:
        return output  # No purple

    # Horizontal fills for each purple row
    for pr in range(min_r, max_r + 1):
        # Left
        for c in range(min_c - 1, -1, -1):
            if grid[pr][c] == 1 or grid[pr][c] == 8:
                break
            output[pr][c] = 4
        # Right
        for c in range(max_c + 1, cols):
            if grid[pr][c] == 1 or grid[pr][c] == 8:
                break
            output[pr][c] = 4

    # Vertical fills for each purple column
    for pc in range(min_c, max_c + 1):
        # Up
        for r in range(min_r - 1, -1, -1):
            if grid[r][pc] == 1 or grid[r][pc] == 8:
                break
            output[r][pc] = 4
        # Down
        for r in range(max_r + 1, rows):
            if grid[r][pc] == 1 or grid[r][pc] == 8:
                break
            output[r][pc] = 4

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
