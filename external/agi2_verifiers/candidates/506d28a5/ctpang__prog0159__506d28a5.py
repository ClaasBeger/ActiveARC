"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 506d28a5
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[159](id=159)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0159__506d28a5
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid_lst: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid_lst)
    height, width = grid.shape
    middle = height // 2
    upper = grid[0:middle, :]
    lower = grid[middle + 1:, :]
    out = np.zeros((middle, width), dtype=int)
    diff = upper != lower
    out[diff] = 3
    return out.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
