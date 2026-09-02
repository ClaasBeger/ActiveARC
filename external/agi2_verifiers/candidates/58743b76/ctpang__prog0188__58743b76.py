"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 58743b76
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[188](id=188)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0188__58743b76
"""
from __future__ import annotations



import numpy as np

import copy

def transform(grid: list[list[int]]) -> list[list[int]]:
    out = copy.deepcopy(grid)
    rows = len(grid)
    cols = len(grid[0])
    
    # Find palette position
    palette_r = -1
    palette_c = -1
    for r in range(rows - 1):
        for c in range(cols - 1):
            if all(grid[r + i][c + j] > 0 and grid[r + i][c + j] != 8 for i in [0, 1] for j in [0, 1]):
                palette_r = r
                palette_c = c
                break
        if palette_r != -1:
            break
    
    if palette_r == -1:
        return out
    
    # Get palette colors
    tl = grid[palette_r][palette_c]
    tr = grid[palette_r][palette_c + 1]
    bl = grid[palette_r + 1][palette_c]
    br = grid[palette_r + 1][palette_c + 1]
    
    # Determine canvas bounds
    frame_rows_start = palette_r
    frame_cols_start = palette_c
    
    if frame_rows_start == 0:
        canvas_row_start = 2
        canvas_row_end = rows - 1
    else:
        canvas_row_start = 0
        canvas_row_end = rows - 3
    
    if frame_cols_start == 0:
        canvas_col_start = 2
        canvas_col_end = cols - 1
    else:
        canvas_col_start = 0
        canvas_col_end = cols - 3
    
    # Canvas dimensions
    height = canvas_row_end - canvas_row_start + 1
    width = canvas_col_end - canvas_col_start + 1
    half_h = height // 2
    half_w = width // 2
    
    # Recolor non-zero cells in canvas
    for r in range(canvas_row_start, canvas_row_end + 1):
        for c in range(canvas_col_start, canvas_col_end + 1):
            if grid[r][c] != 0:
                local_r = r - canvas_row_start
                local_c = c - canvas_col_start
                if local_r < half_h:
                    if local_c < half_w:
                        new_color = tl
                    else:
                        new_color = tr
                else:
                    if local_c < half_w:
                        new_color = bl
                    else:
                        new_color = br
                out[r][c] = new_color
    
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
