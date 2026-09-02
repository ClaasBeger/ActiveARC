"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 2b01abd0
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[87](id=87)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0087__2b01abd0
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    
    # Find mirror row or column
    mirror_row = -1
    for i in range(rows):
        if all(grid[i][j] == 1 for j in range(cols)):
            mirror_row = i
            break
    
    mirror_col = -1
    for j in range(cols):
        if all(grid[i][j] == 1 for i in range(rows)):
            mirror_col = j
            break
    
    # Collect original shape positions and colors
    original_shape = []
    color_set = set()
    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]
            if val != 0 and val != 1:
                original_shape.append((r, c, val))
                color_set.add(val)
    
    # Assume exactly two colors
    if len(color_set) != 2:
        return grid  # Or handle differently, but per puzzle it's 2
    c1, c2 = list(color_set)
    
    def swap(col):
        if col == c1:
            return c2
        if col == c2:
            return c1
        return col
    
    # Create output grid
    output = [row[:] for row in grid]
    
    # Add reflections
    if mirror_col != -1:
        for r, c, val in original_shape:
            mir_c = 2 * mirror_col - c
            if 0 <= mir_c < cols:
                output[r][mir_c] = val
    elif mirror_row != -1:
        for r, c, val in original_shape:
            mir_r = 2 * mirror_row - r
            if 0 <= mir_r < rows:
                output[mir_r][c] = val
    
    # Swap colors in original positions
    for r, c, val in original_shape:
        output[r][c] = swap(val)
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
