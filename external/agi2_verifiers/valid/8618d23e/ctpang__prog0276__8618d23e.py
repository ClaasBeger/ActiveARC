"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 8618d23e
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[276](id=276)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0276__8618d23e
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    h = len(grid)
    w = len(grid[0])
    half = h // 2
    out_h = h + 1
    out_w = w + 1
    output = [[0 for _ in range(out_w)] for _ in range(out_h)]
    
    # Place top half with 9 appended to each row
    for i in range(half):
        for j in range(w):
            output[i][j] = grid[i][j]
        output[i][w] = 9
    
    # Separator row of 9's
    for j in range(out_w):
        output[half][j] = 9
    
    # Place bottom half with 9 prepended to each row
    for i in range(half):
        output[half + 1 + i][0] = 9
        for j in range(w):
            output[half + 1 + i][j + 1] = grid[half + i][j]
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
