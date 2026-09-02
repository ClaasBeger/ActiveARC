"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e4941b18
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[484](id=484)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0484__e4941b18
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    
    # Find purple (8) and red (2) positions
    pr, pc = None, None
    rr, rc = None, None
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 8:
                pr, pc = r, c
            elif grid[r][c] == 2:
                rr, rc = r, c
    
    if pr is None or rr is None:
        return grid  # No change if missing
    
    # Determine slide direction opposite to red
    dir_sign = 1 if rc < pc else -1
    
    # Find slide column
    step = 1
    new_c = None
    while True:
        candidate_c = pc + step * dir_sign
        if candidate_c < 0 or candidate_c >= cols:
            break  # Should not happen based on examples
        if pr + 1 < rows and grid[pr + 1][candidate_c] == 7:
            new_c = candidate_c
            break
        step += 1
    
    if new_c is None:
        return grid  # No valid position, though unlikely
    
    # Fall down in new_c
    r = pr + 1
    while r < rows and grid[r][new_c] == 7:
        r += 1
    new_pr = r - 1
    
    # Create output
    output = [row[:] for row in grid]
    
    # Move red to old purple position
    output[pr][pc] = 2
    
    # Set old red to 7
    output[rr][rc] = 7
    
    # Set new purple position
    output[new_pr][new_c] = 8
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
