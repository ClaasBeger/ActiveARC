"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e7b06bea
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[494](id=494)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0494__e7b06bea
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    rows, cols = grid.shape
    
    # Find height h of grey (5) in column 0
    grey_col = 0
    h = 0
    for r in range(rows):
        if grid[r, grey_col] == 5:
            h += 1
        else:
            break
    
    # Find start_col of right uniform bars
    start_col = cols
    for c in range(cols - 1, -1, -1):
        color = grid[0, c]
        if color == 0:
            break
        is_uniform = all(grid[r, c] == color for r in range(rows))
        if not is_uniform:
            break
        start_col = c
    
    # Collect colors sequence
    colors = [grid[0, c] for c in range(start_col, cols)]
    k = len(colors)
    if k == 0:
        return grid.tolist()
    
    new_col = start_col - 1
    output = grid.copy()
    
    # Clear original right bars
    for c in range(start_col, cols):
        for r in range(rows):
            output[r, c] = 0
    
    # Place new bar
    for r in range(rows):
        seg = r // h
        idx = seg % k
        output[r, new_col] = colors[idx]
    
    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
