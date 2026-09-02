"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 3d6c6e23
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[122](id=122)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0122__3d6c6e23
"""
from __future__ import annotations



import numpy as np

import math

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    height = len(grid)
    width = len(grid[0])
    output = [[0 for _ in range(width)] for _ in range(height)]
    
    for c in range(width):
        seq = []
        for r in range(height):
            if grid[r][c] != 0:
                seq.append(grid[r][c])
        
        n = len(seq)
        if n == 0:
            continue
        
        h = int(math.sqrt(n))
        if h * h != n:
            raise ValueError("Number of cells is not a perfect square")
        
        idx = 0
        for k in range(1, h + 1):
            py_r = height - h + (k - 1)
            w = 2 * k - 1
            left = c - (w // 2)
            for j in range(w):
                col_pos = left + j
                if 0 <= col_pos < width:
                    output[py_r][col_pos] = seq[idx]
                idx += 1
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
