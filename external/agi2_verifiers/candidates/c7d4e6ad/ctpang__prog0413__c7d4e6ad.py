"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: c7d4e6ad
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[413](id=413)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0413__c7d4e6ad
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    rows = len(grid)
    cols = len(grid[0])
    output = [row[:] for row in grid]
    
    for r in range(rows):
        color = 0
        for c in range(cols):
            if grid[r][c] != 0 and grid[r][c] != 5:
                color = grid[r][c]
                break
        if color != 0:
            for c in range(cols):
                if grid[r][c] == 5:
                    output[r][c] = color
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
