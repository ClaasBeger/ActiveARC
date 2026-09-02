"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 27a77e38
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[80](id=80)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0080__27a77e38
"""
from __future__ import annotations



import numpy as np

import copy
from collections import Counter

def transform(grid: list[list[int]]) -> list[list[int]]:
    out = copy.deepcopy(grid)
    rows = len(grid)
    cols = len(grid[0])
    
    # Find the gray row (all 5s)
    gray_row = -1
    for r in range(rows):
        if all(cell == 5 for cell in grid[r]):
            gray_row = r
            break
    
    if gray_row == -1:
        return out  # No gray row, no change (though assumes there is one)
    
    # Collect all colors in colored rows (0 to gray_row-1)
    color_counts = Counter()
    for r in range(gray_row):
        for c in range(cols):
            colr = grid[r][c]
            if colr != 0:  # Though in colored rows, all non-zero
                color_counts[colr] += 1
    
    if not color_counts:
        return out
    
    # Find the color with max frequency
    max_color = max(color_counts, key=color_counts.get)
    
    # Bottom row
    bottom_row = rows - 1
    
    # Center column
    center_col = (cols - 1) // 2
    
    # Set the cell
    out[bottom_row][center_col] = max_color
    
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
