"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 3cd86f4f
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[121](id=121)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0121__3cd86f4f
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    h = len(grid)
    w = len(grid[0])
    out_w = w + h - 1
    output = [[0] * out_w for _ in range(h)]
    
    for r in range(h):
        left_zeros = h - 1 - r
        for c in range(w):
            output[r][left_zeros + c] = grid[r][c]
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
