"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: fd02da9e
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[535](id=535)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0535__fd02da9e
"""
from __future__ import annotations



import numpy as np

import copy

def transform(grid: list[list[int]]) -> list[list[int]]:
    output = copy.deepcopy(grid)
    height = len(grid)
    width = len(grid[0])
    
    # Top-left corner
    if grid[0][0] != 7:
        c = grid[0][0]
        output[0][0] = 7
        output[1][1] = c
        output[1][2] = c
        output[2][1] = c
        output[2][2] = c
    
    # Top-right corner
    if grid[0][width-1] != 7:
        c = grid[0][width-1]
        output[0][width-1] = 7
        output[1][5] = c
        output[1][6] = c
        output[2][5] = c
        output[2][6] = c
    
    # Bottom-left corner
    if grid[height-1][0] != 7:
        c = grid[height-1][0]
        output[height-1][0] = 7
        output[4][2] = c
        output[5][2] = c
        output[6][3] = c
    
    # Bottom-right corner
    if grid[height-1][width-1] != 7:
        c = grid[height-1][width-1]
        output[height-1][width-1] = 7
        output[4][5] = c
        output[5][5] = c
        output[6][4] = c
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
