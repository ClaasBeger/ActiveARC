"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 12422b43
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[25](id=25)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0025__12422b43
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    
    # Find h: number of consecutive 5's in column 0 from top
    h = 0
    for r in range(rows):
        if grid[r][0] == 5:
            h += 1
        else:
            break
    
    # Find the last row with any non-zero cell
    initial_last = 0
    for r in range(rows):
        if any(grid[r][c] != 0 for c in range(cols)):
            initial_last = r
    initial_height = initial_last + 1
    
    # Calculate remaining rows and number of full repetitions
    remaining = rows - initial_height
    reps = remaining // h
    
    # Perform the repetitions
    for i in range(reps):
        for j in range(h):
            target_r = initial_height + i * h + j
            for c in range(cols):
                if c == 0:
                    grid[target_r][c] = 0
                else:
                    grid[target_r][c] = grid[j][c]
    
    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
