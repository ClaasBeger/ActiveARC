"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 31d5ba1a
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__31d5ba1a
"""
from __future__ import annotations



import numpy as np

def solve_31d5ba1a(input_grid):
    """
    Concepts: Two halves of a grid, Double controlled gate logic using two halves of a grid

    Transformation steps:
    1. Split the grid into top_half and bottom_half 
    Looing at training examples, we see that:
     - there are two halves of a grid, each have two unique values (0, 4) and (9, 0).
     - the following mapping
    2. For each cell in the top_half, pair it with the corresponding cell in the bottom_half.
    3. Use a mapping to determine the output value for each cell based on the pair:
       - (0, 0) -> 0
       - (0, 4) -> 6
       - (9, 0) -> 6
       - (9, 4) -> 0
    4. Construct the output grid using these mapped values.
    """
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape

    top_half = input_grid[: nrows//2]            # Step 1: Get the top half 
    bottom_half = input_grid[nrows//2 :]         # Step 1: Get the bottom half 

    # Step 2 and 3: Mapping for output values based on paired cells
    value_map = {(0, 0): 0, (0, 4): 6, (9, 0): 6, (9, 4): 0}
    output_grid = np.zeros_like(top_half, dtype=int)

    for r in range(top_half.shape[0]):
        for c in range(ncols): # Step 4: Construct the output grid using the mapping
            output_grid[r, c] = value_map[(top_half[r, c], bottom_half[r, c])]

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_31d5ba1a(input_grid)
    return _result
