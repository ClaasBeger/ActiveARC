"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 29700607
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[84](id=84)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0084__29700607
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    
    # Find heads in row 0
    head_col = {}
    for c in range(cols):
        color = grid[0][c]
        if color != 0:
            head_col[color] = c
    
    # Find tails
    tail = {}
    for r in range(1, rows):
        for c in range(cols):
            color = grid[r][c]
            if color != 0:
                tail[color] = (r, c)
    
    # Create output grid
    output = [row[:] for row in grid]
    
    # Fill for each color
    for color, h_col in head_col.items():
        if color in tail:
            t_r, t_c = tail[color]
            # Vertical fill
            for rr in range(t_r + 1):
                output[rr][h_col] = color
            # Horizontal fill
            min_c = min(h_col, t_c)
            max_c = max(h_col, t_c)
            for cc in range(min_c, max_c + 1):
                output[t_r][cc] = color
        else:
            # Vertical to bottom
            for rr in range(rows):
                output[rr][h_col] = color
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
