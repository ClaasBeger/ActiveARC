"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 5b6cbef5
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__5b6cbef5
"""
from __future__ import annotations



import numpy as np

def solve_5b6cbef5(input_grid):
    """
    Create a larger grid by tiling the input grid based on non-zero cells. (similar to Koch curve)
 
    Concept:
    - non-zero cell analysis
    - tiling with input grid
 
    Transformation Steps:
        1. Initialize a large output grid of size (nrows**2, ncols**2).
        2. For each non-zero cell in the input grid, copy the entire input grid into the corresponding tile in the output grid.
    """
 
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = np.zeros((nrows**2, ncols**2), dtype=int)
 
    for r in range(nrows):
        for c in range(ncols):
            if input_grid[r, c] != 0:
                output_grid[r*nrows:(r+1)*nrows, c*ncols:(c+1)*ncols] = input_grid
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_5b6cbef5(input_grid)
    return _result
