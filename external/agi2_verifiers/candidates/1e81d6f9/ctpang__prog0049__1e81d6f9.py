"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 1e81d6f9
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[49](id=49)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0049__1e81d6f9
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    output = [row[:] for row in grid]
    special_row = 1
    special_col = 1
    c = grid[special_row][special_col]
    if c == 0:
        return output
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == c and (i != special_row or j != special_col):
                output[i][j] = 0
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
