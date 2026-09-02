"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 575b1a71
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[185](id=185)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0185__575b1a71
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    rows = len(grid)
    cols = len(grid[0])
    
    # Find unique columns with at least one 0
    col_set = set()
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                col_set.add(c)
    
    # Sort the columns
    sorted_cols = sorted(col_set)
    
    # Assign colors: column to color (1 + index)
    col_to_color = {col: idx + 1 for idx, col in enumerate(sorted_cols)}
    
    # Create output grid
    output = [row[:] for row in grid]
    
    # Replace 0s with the assigned color for their column
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                output[r][c] = col_to_color[c]
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
