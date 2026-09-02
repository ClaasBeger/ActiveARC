"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: a8610ef7
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__a8610ef7
"""
from __future__ import annotations



import numpy as np

def solve_a8610ef7(input_grid):
    """
    Concepts: vertical symmetry (up-down flip), value replacement based on symmetry

    Transformation steps:
    1. Loop through each cell in the grid.
    2. If value is 0, retain as 0.
    3. If value is 8:
        - Check vertically mirrored cell (i.e., up-down symmetric).
        - If mirrored cell also contains 8, change to 2.
        - Otherwise, change to 5.
    """
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = np.zeros_like(input_grid) # Initialize output grid with zeros
    
    for i in range(nrows):
        for j in range(ncols):
            if input_grid[i, j] == 8: # Step 3: check for value 8
                mirror_i = nrows - 1 - i
                if input_grid[mirror_i, j] == 8: # check for vertical symmetry 
                    output_grid[i, j] = 2        # if symmetric, change to 2
                else:
                    output_grid[i, j] = 5        # if not symmetric, change to 5
            else:
                output_grid[i, j] = input_grid[i, j]
    
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_a8610ef7(input_grid)
    return _result
