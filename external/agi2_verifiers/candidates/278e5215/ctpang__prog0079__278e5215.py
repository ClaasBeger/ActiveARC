"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 278e5215
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[79](id=79)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0079__278e5215
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    rows = len(grid)
    cols = len(grid[0])
    
    # Find bar rows
    bar_rows = [i for i in range(rows) if any(c > 0 and c != 5 for c in grid[i])]
    
    if not bar_rows:
        return grid  # No transformation if no bar
    
    min_bar = min(bar_rows)
    max_bar = max(bar_rows)
    
    # Uniform row is the last one
    uniform_row = max_bar
    non_zeros = {c for c in grid[uniform_row] if c != 0}
    if len(non_zeros) != 1:
        raise ValueError("Uniform row has multiple non-zero colors")
    C = list(non_zeros)[0]
    
    # Mixed row
    mixed_row = min_bar
    js = [j for j in range(cols) if grid[mixed_row][j] != 0]
    if not js:
        raise ValueError("No colors in mixed row")
    min_j = min(js)
    max_j = max(js)
    if len(js) != max_j - min_j + 1:
        raise ValueError("Colors in mixed row are not contiguous")
    S = [grid[mixed_row][j] for j in range(min_j, max_j + 1)]
    
    # Find grey bounding box
    grey_pos = [(i, j) for i in range(rows) for j in range(cols) if grid[i][j] == 5]
    if not grey_pos:
        return grid  # No transformation if no grey
    
    min_r = min(i for i, j in grey_pos)
    max_r = max(i for i, j in grey_pos)
    min_c = min(j for i, j in grey_pos)
    max_c = max(j for i, j in grey_pos)
    
    height = max_r - min_r + 1
    width = max_c - min_c + 1
    
    if len(S) != width:
        raise ValueError("Length of S does not match width")
    
    # Create output
    output = [[0] * width for _ in range(height)]
    for sub_i in range(height):
        for sub_j in range(width):
            actual_i = min_r + sub_i
            actual_j = min_c + sub_j
            if grid[actual_i][actual_j] == 5:
                output[sub_i][sub_j] = S[sub_j]
            else:
                output[sub_i][sub_j] = C
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
