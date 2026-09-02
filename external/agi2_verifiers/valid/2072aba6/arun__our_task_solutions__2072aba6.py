"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 2072aba6
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__2072aba6
"""
from __future__ import annotations



import numpy as np

def solve_2072aba6(input_grid):
    """
    Concepts: 

    Transformation steps:
    1. Initialize an output grid of size (2×nrows, 2×ncols) filled with zeros.
       - This will be twice the size of the input grid.
    2. For each cell in the input grid,
       - if it contains non-zero value 5, replace the corresponding block in the output grid with 2x2 non-zero block [[1, 2], [2, 1]].
    """
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape

    # Step 1: Initialize output grid of size (2×nrows, 2×ncols)
    output_grid = np.zeros((2 * nrows, 2 * ncols), dtype=int)

    non_zero_block = np.array([[1, 2], [2, 1]], dtype=int)

    for i in range(nrows):
        for j in range(ncols):
            r, c = 2 * i, 2 * j
            if input_grid[i, j] == 5: # Step 2: if the input cell is 5
                # Place the non-zero block in the corresponding position in the output grid
                output_grid[r:r+2, c:c+2] = non_zero_block

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_2072aba6(input_grid)
    return _result
