"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 140c817e
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[31](id=31)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0031__140c817e
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    height = len(grid)
    width = len(grid[0])
    
    # Find seed positions (where color is 1)
    seeds = []
    for r in range(height):
        for c in range(width):
            if grid[r][c] == 1:
                seeds.append((r, c))
    
    # Create output grid as copy
    output = [row[:] for row in grid]
    
    # Set the crosses for each seed
    for r, c in seeds:
        # Set the entire row to 1, center to 2
        for j in range(width):
            output[r][j] = 1
        output[r][c] = 2
        
        # Set the entire column to 1 (skip center as it's already 2)
        for i in range(height):
            if i != r:
                output[i][c] = 1
    
    # Set the green diagonals for each seed
    for r, c in seeds:
        for dr in [-1, 1]:
            for dc in [-1, 1]:
                nr = r + dr
                nc = c + dc
                if 0 <= nr < height and 0 <= nc < width:
                    output[nr][nc] = 3
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
