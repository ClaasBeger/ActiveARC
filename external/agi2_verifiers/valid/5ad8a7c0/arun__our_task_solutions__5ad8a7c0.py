"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 5ad8a7c0
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__5ad8a7c0
"""
from __future__ import annotations



import numpy as np

def solve_5ad8a7c0(input_grid):
    """
    Concepts: 2D grid manipulation, mirroring, Pattern filling

    Transformation steps:
    1. Split the input grid into left and right halves.
    2. Find all positions of the color '2' in the left half.
    3. Identify the last column position of '2' in the left half.
    4. Create a copy of the left half input grid for output.
    5. For each row with '2' in the last column, fill all cells to the right with '2'.
    6. Mirror the left half to create the right half.
    7. Combine the left and right halves to form the output grid.
    """
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape

    half_ncols = ncols // 2
    # Step 1: Split the input grid into left and right halves
    left_half_input = input_grid[:, :half_ncols]
    
    # Step 2: Find all positions of the color '2' in the left half
    rows, cols = np.where(left_half_input == 2)

    # Step 3: Identify the last column position of '2' in the left half
    max_col = cols.max() if len(cols) > 0 else -1
    last_col_indices = np.where(cols == max_col)[0]

    # Step 4: Create a copy of the left half input grid for output
    left_half_output  = left_half_input.copy()
    for idx in last_col_indices:
        r, c = rows[idx], cols[idx]
        left_half_output[r, c+1 : half_ncols] = 2# Step 5: Fill the right side of the row with '2'

    right_half_output = np.fliplr(left_half_output) # Step 6: Mirror the left half to create the right half
    
    # Step 7: Combine the left and right halves to form the output grid
    output_grid = np.hstack([left_half_output, right_half_output])    

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_5ad8a7c0(input_grid)
    return _result
