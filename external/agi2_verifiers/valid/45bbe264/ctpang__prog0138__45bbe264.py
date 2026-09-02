"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 45bbe264
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[138](id=138)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0138__45bbe264
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    height = len(grid)
    width = len(grid[0])
    output = [[0 for _ in range(width)] for _ in range(height)]
    
    # Find seeds and map rows and columns to colors
    row_to_color = {}
    col_to_color = {}
    for r in range(height):
        for c in range(width):
            color = grid[r][c]
            if color != 0:
                row_to_color[r] = color
                col_to_color[c] = color
    
    # Set vertical lines
    for c, color in col_to_color.items():
        for r in range(height):
            output[r][c] = color
    
    # Set horizontal lines with overrides for conflicts
    for r, color in row_to_color.items():
        for c in range(width):
            existing = output[r][c]
            if existing != 0 and existing != color:
                output[r][c] = 2
            else:
                output[r][c] = color
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
