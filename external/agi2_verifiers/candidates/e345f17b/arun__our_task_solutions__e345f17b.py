"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e345f17b
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__e345f17b
"""
from __future__ import annotations



import numpy as np

def solve_e345f17b(input_grid):
    """
    Concepts: Two halves of a grid, addition of grid, conditional replacement of value

    Transformation steps:
    1. Split the grid into top_half and bottom_half 
    2. Add the two halves together
    3. If the sum of the two halves is 0, then output 4, else output 0
    """
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape

    left_half = input_grid[:, : ncols//2]            # Step 1: Get the left half 
    right_half = input_grid[:, ncols//2 :]           # Step 1: Get the right half 

    # Step 2: add the two halves together
    added = left_half + right_half
    # Step 3: If the sum of the two halves is 0, then output 4, else output 0
    output_grid = np.where(added == 0, 4, 0)
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_e345f17b(input_grid)
    return _result
