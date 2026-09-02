"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e7dd8335
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[495](id=495)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0495__e7dd8335
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    grid = np.array(grid)
    rows, cols = grid.shape
    
    # Find min_r and max_r
    non_zero_rows = np.where(np.any(grid != 0, axis=1))[0]
    if len(non_zero_rows) == 0:
        return grid.tolist()
    min_r = np.min(non_zero_rows)
    max_r = np.max(non_zero_rows)
    
    H = max_r - min_r + 1
    split = H // 2
    bottom_start = min_r + (H - split)
    
    # Copy grid
    output = grid.copy()
    
    # Change 1 to 2 in bottom rows
    for r in range(bottom_start, max_r + 1):
        for c in range(cols):
            if output[r, c] == 1:
                output[r, c] = 2
    
    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
