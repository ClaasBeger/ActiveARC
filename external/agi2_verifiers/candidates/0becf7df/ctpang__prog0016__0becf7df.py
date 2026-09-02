"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 0becf7df
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[16](id=16)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0016__0becf7df
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or len(grid) < 2 or len(grid[0]) < 2:
        return grid
    
    output = [row[:] for row in grid]
    
    A = grid[0][0]
    B = grid[0][1]
    C = grid[1][0]
    D = grid[1][1]
    
    swap = {A: B, B: A, C: D, D: C}
    
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            # Skip key positions
            if (r == 0 and c in (0, 1)) or (r == 1 and c in (0, 1)):
                continue
            if grid[r][c] != 0:
                output[r][c] = swap.get(grid[r][c], grid[r][c])
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
