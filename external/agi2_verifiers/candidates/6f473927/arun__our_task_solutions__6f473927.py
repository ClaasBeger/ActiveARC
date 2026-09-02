"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 6f473927
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__6f473927
"""
from __future__ import annotations



import numpy as np

def solve_6f473927(input_grid):
    """
    Concepts: Grid transformation (negative of the positive photograph) with flipping and stacking.

    Transformation steps:
    1. Identify positions of zero and non-zero values in the input grid.
    2. Replace zeros with 8 and non-zero values with 0 in a copy of the input grid.
    3. Flip the modified grid horizontally.
    4. Depending on the position of non-zero values:
       - If non-zero values are on the left in input, stack the flipped grid to the left of the original grid.
       - If non-zero values are on the right in input, stack the flipped grid to the right of the original grid.
    """

    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape

    # Identify positions of zeros and non-zeros
    pos_with_0 = np.argwhere(input_grid == 0)
    pos_without_0 = np.argwhere(input_grid != 0)
    min_col, max_col = pos_without_0[:, 1].min(), pos_without_0[:, 1].max()

    # Create a modified version of the input grid (negative of the positive photograph)
    half_output = input_grid.copy()
    half_output[pos_with_0[:, 0], pos_with_0[:, 1]] = 8
    half_output[pos_without_0[:, 0], pos_without_0[:, 1]] = 0

    # Flip the modified grid horizontally
    half_output = np.fliplr(half_output)

    # Stack grids based on the position of non-zero values
    if min_col == 0:  # Non-zero values are on the left
        output_grid = np.hstack([half_output, input_grid])
    elif max_col == ncols - 1:  # Non-zero values are on the right
        output_grid = np.hstack([input_grid, half_output])

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_6f473927(input_grid)
    return _result
