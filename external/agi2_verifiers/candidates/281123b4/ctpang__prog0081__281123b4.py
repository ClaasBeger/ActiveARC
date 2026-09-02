"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 281123b4
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[81](id=81)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0081__281123b4
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    # Extract the four 4x4 sections
    purple = [row[0:4] for row in grid]
    gray = [row[5:9] for row in grid]
    brown = [row[10:14] for row in grid]
    yellow = [row[15:19] for row in grid]
    
    # Create output 4x4 grid
    output = [[0 for _ in range(4)] for _ in range(4)]
    
    for i in range(4):
        for j in range(4):
            if brown[i][j] != 0:
                output[i][j] = 9
            elif yellow[i][j] != 0:
                output[i][j] = 4
            elif purple[i][j] != 0:
                output[i][j] = 8
            elif gray[i][j] != 0:
                output[i][j] = 5
            # else remains 0
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
