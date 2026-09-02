"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e7a25a18
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[493](id=493)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0493__e7a25a18
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    rows = len(grid)
    cols = len(grid[0])
    
    # Find outer bounding box of 2's
    outer_min_r, outer_max_r = rows, -1
    outer_min_c, outer_max_c = cols, -1
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                outer_min_r = min(outer_min_r, r)
                outer_max_r = max(outer_max_r, r)
                outer_min_c = min(outer_min_c, c)
                outer_max_c = max(outer_max_c, c)
    
    if outer_min_r > outer_max_r:
        return []  # No frame, but assume there is
    
    outer_h = outer_max_r - outer_min_r + 1
    outer_w = outer_max_c - outer_min_c + 1
    inner_h = outer_h - 2
    inner_w = outer_w - 2
    
    # Find minimal bounding box of inner colors (!=0 and !=2)
    colored_min_r, colored_max_r = rows, -1
    colored_min_c, colored_max_c = cols, -1
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and grid[r][c] != 2:
                colored_min_r = min(colored_min_r, r)
                colored_max_r = max(colored_max_r, r)
                colored_min_c = min(colored_min_c, c)
                colored_max_c = max(colored_max_c, c)
    
    if colored_min_r > colored_max_r:
        # No colors, but assume there are
        pass
    
    colored_h = colored_max_r - colored_min_r + 1
    colored_w = colored_max_c - colored_min_c + 1
    
    scale_h = inner_h // colored_h
    scale_w = inner_w // colored_w
    
    # Extract colored subgrid
    colored_grid = []
    for i in range(colored_h):
        row = [grid[colored_min_r + i][colored_min_c + j] for j in range(colored_w)]
        colored_grid.append(row)
    
    # Scale it
    scaled_inner = []
    for i in range(colored_h):
        orig_row = colored_grid[i]
        scaled_row = []
        for val in orig_row:
            scaled_row.extend([val] * scale_w)
        for _ in range(scale_h):
            scaled_inner.append(scaled_row)
    
    # Create output
    output = [[0] * outer_w for _ in range(outer_h)]
    
    # Set border to 2
    for c in range(outer_w):
        output[0][c] = 2
        output[outer_h - 1][c] = 2
    for r in range(outer_h):
        output[r][0] = 2
        output[r][outer_w - 1] = 2
    
    # Place scaled inner
    for ri in range(inner_h):
        for ci in range(inner_w):
            output[1 + ri][1 + ci] = scaled_inner[ri][ci]
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
