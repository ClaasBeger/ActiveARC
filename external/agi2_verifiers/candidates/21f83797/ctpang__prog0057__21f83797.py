"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 21f83797
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[57](id=57)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0057__21f83797
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    height = len(grid)
    width = len(grid[0])
    
    # Find seeds where color is 2
    seeds = [(i, j) for i in range(height) for j in range(width) if grid[i][j] == 2]
    
    if not seeds:
        return [row[:] for row in grid]
    
    # Collect unique rows and columns
    horiz_rows = set(r for r, c in seeds)
    vert_cols = set(c for r, c in seeds)
    
    # Create output grid initialized to 0
    output = [[0 for _ in range(width)] for _ in range(height)]
    
    # Draw horizontal red lines
    for r in horiz_rows:
        for j in range(width):
            output[r][j] = 2
    
    # Draw vertical red lines
    for c in vert_cols:
        for i in range(height):
            output[i][c] = 2
    
    # Fill interior with blue (1) if possible
    if len(horiz_rows) >= 2 and len(vert_cols) >= 2:
        min_r = min(horiz_rows)
        max_r = max(horiz_rows)
        min_c = min(vert_cols)
        max_c = max(vert_cols)
        for i in range(min_r + 1, max_r):
            for j in range(min_c + 1, max_c):
                output[i][j] = 1
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
