"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: d2acf2cb
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[440](id=440)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0440__d2acf2cb
"""
from __future__ import annotations



import numpy as np

import copy

def transform(grid: list[list[int]]) -> list[list[int]]:
    output = copy.deepcopy(grid)
    if not grid or not grid[0]:
        return output
    rows = len(grid)
    cols = len(grid[0])
    
    # Toggle horizontal
    for i in range(rows):
        if grid[i][0] == 4 and grid[i][cols-1] == 4:
            for j in range(1, cols-1):
                c = output[i][j]
                if c == 0:
                    output[i][j] = 8
                elif c == 8:
                    output[i][j] = 0
                elif c == 6:
                    output[i][j] = 7
                elif c == 7:
                    output[i][j] = 6
    
    # Toggle vertical
    for j in range(cols):
        if grid[0][j] == 4 and grid[rows-1][j] == 4:
            for i in range(1, rows-1):
                c = output[i][j]
                if c == 0:
                    output[i][j] = 8
                elif c == 8:
                    output[i][j] = 0
                elif c == 6:
                    output[i][j] = 7
                elif c == 7:
                    output[i][j] = 6
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
