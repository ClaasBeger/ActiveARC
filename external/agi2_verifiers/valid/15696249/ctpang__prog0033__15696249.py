"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 15696249
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[33](id=33)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0033__15696249
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    n = 3
    out = np.zeros((3 * n, 3 * n), dtype=int)
    grid_np = np.array(grid)
    
    # Check for monochromatic rows
    mono_row = -1
    for i in range(n):
        if np.all(grid_np[i, :] == grid_np[i, 0]):
            mono_row = i
            break
    
    if mono_row != -1:
        # Horizontal tiling in super row mono_row
        for ii in range(n):
            for jj in range(3 * n):
                out[3 * mono_row + ii, jj] = grid_np[ii, jj % n]
    else:
        # Check for monochromatic columns
        mono_col = -1
        for j in range(n):
            if np.all(grid_np[:, j] == grid_np[0, j]):
                mono_col = j
                break
        if mono_col != -1:
            # Vertical tiling in super column mono_col
            for jj in range(n):
                for ii in range(3 * n):
                    out[ii, 3 * mono_col + jj] = grid_np[ii % n, jj]
    
    return out.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
