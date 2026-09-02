"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 833dafe3
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[267](id=267)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0267__833dafe3
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid_lst: list[list[int]]) -> list[list[int]]:
    if not grid_lst or not grid_lst[0]:
        return []
    grid = np.array(grid_lst)
    n = grid.shape[0]
    # 180 degree rotation
    rotated = np.rot90(grid, 2)
    # Create output grid
    out = np.zeros((2 * n, 2 * n), dtype=int)
    # Top-left
    out[0:n, 0:n] = rotated
    # Top-right: horizontal flip of top-left
    out[0:n, n:2*n] = np.fliplr(out[0:n, 0:n])
    # Bottom-left: vertical flip of top-left
    out[n:2*n, 0:n] = np.flipud(out[0:n, 0:n])
    # Bottom-right: horizontal flip of bottom-left
    out[n:2*n, n:2*n] = np.fliplr(out[n:2*n, 0:n])
    return out.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
