"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: fc754716
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[533](id=533)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0533__fc754716
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    h = len(grid)
    w = len(grid[0])
    
    # Find the color C of the single non-zero cell
    C = None
    for r in range(h):
        for c in range(w):
            if grid[r][c] != 0:
                if C is not None:
                    raise ValueError("Multiple non-zero cells found")
                C = grid[r][c]
    
    if C is None:
        raise ValueError("No non-zero cell found")
    
    # Create new grid of zeros
    new_grid = [[0 for _ in range(w)] for _ in range(h)]
    
    # Set top and bottom rows to C
    for c in range(w):
        new_grid[0][c] = C
        new_grid[h-1][c] = C
    
    # Set left and right columns to C (excluding top and bottom already set)
    for r in range(1, h-1):
        new_grid[r][0] = C
        new_grid[r][w-1] = C
    
    return new_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
