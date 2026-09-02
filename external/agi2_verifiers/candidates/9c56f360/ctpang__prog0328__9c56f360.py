"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9c56f360
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[328](id=328)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0328__9c56f360
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    output = [row[:] for row in grid]
    rows = len(grid)
    cols = len(grid[0])
    for r in range(rows):
        # Find rightmost purple (8)
        rightmost_purple = -1
        for c in range(cols):
            if grid[r][c] == 8:
                rightmost_purple = c
        target_start = 0 if rightmost_purple == -1 else rightmost_purple + 1
        
        # Find the green block: min and max c with 3
        green_cols = [c for c in range(cols) if grid[r][c] == 3]
        if not green_cols:
            continue
        min_c = min(green_cols)
        max_c = max(green_cols)
        length = max_c - min_c + 1
        # Assume contiguous, as in examples
        
        # Clear original
        for c in range(min_c, max_c + 1):
            output[r][c] = 0
        
        # Set new positions, if within bounds
        if target_start + length > cols:
            # Doesn't happen in examples, but to handle, perhaps truncate or something, but assume fits
            pass
        for c in range(target_start, target_start + length):
            if c < cols:
                output[r][c] = 3
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
