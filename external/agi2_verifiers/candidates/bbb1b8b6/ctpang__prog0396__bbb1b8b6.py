"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: bbb1b8b6
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[396](id=396)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0396__bbb1b8b6
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    
    h = len(grid)
    w = len(grid[0])
    
    # Find gray column
    gray_col = -1
    for c in range(w):
        if all(grid[r][c] == 5 for r in range(h)):
            gray_col = c
            break
    if gray_col == -1:
        return grid  # Assume there is one; fallback to return grid
    
    left_w = gray_col
    right_start = gray_col + 1
    
    # Left zeros positions
    left_zeros = set()
    for r in range(h):
        for c in range(left_w):
            if grid[r][c] == 0:
                left_zeros.add((r, c))
    
    # Right non-zero positions and color
    right_pos = set()
    colors = set()
    for r in range(h):
        for c in range(right_start, w):
            val = grid[r][c]
            if val != 0:
                colors.add(val)
                rel_c = c - right_start
                right_pos.add((r, rel_c))
    
    color = None
    if len(colors) == 1:
        color = next(iter(colors))
    
    # Create output as copy of left
    output = [row[:left_w] for row in grid]
    
    # If positions match and color exists, fill
    if right_pos == left_zeros and color is not None:
        for r, c in left_zeros:
            output[r][c] = color
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
