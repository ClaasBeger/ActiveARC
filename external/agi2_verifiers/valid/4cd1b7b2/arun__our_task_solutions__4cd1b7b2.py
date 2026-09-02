"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 4cd1b7b2
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__4cd1b7b2
"""
from __future__ import annotations



import numpy as np

def solve_4cd1b7b2(input_grid):
    """
    Concepts: Latin square completion, backtracking

    Transformation steps:
    1. Identify positions of zeros (unfilled cells).
    2. Use backtracking to assign numbers 1–4 to each zero
       such that each row and column contains all numbers 1–4 exactly once.
    """
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape

    # Create the set of digits (colors) to fill in the grid
    digits = {1, 2, 3, 4}
    
    # Recursive backtracking function to fill the grid (Latin square)
    def solve(grid):
        for i in range(nrows):
            for j in range(ncols):
                if grid[i][j] == 0:  # Step 1: Identify positions of zeros (unfilled cells).
                    row_vals = set(grid[i])
                    col_vals = set(grid[:, j])
                    candidates = digits - row_vals - col_vals
                    for val in candidates:
                        grid[i][j] = val
                        if solve(grid):  # Step 2: Recursively try to fill the rest of the grid
                            return True
                        grid[i][j] = 0   # Backtrack if no valid assignment found
                    return False         # No valid value found
        return True  # All cells filled

    output_grid = input_grid.copy()
    solve(output_grid)
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_4cd1b7b2(input_grid)
    return _result
