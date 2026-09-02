"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: aa18de87
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[359](id=359)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0359__aa18de87
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    output = [row[:] for row in grid]
    rows = len(grid)
    cols = len(grid[0])
    
    for r in range(rows):
        pos = [c for c in range(cols) if grid[r][c] != 0]
        if len(pos) < 2:
            continue
        pos.sort()
        for i in range(len(pos) - 1):
            for c in range(pos[i] + 1, pos[i + 1]):
                output[r][c] = 2
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
