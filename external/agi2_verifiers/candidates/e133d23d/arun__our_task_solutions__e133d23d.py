"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e133d23d
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__e133d23d
"""
from __future__ import annotations



import numpy as np

def solve_e133d23d(input_grid):
    """
    Concepts: axis (column) to devide grid in two halves, Two halves of a grid, addition of grid, conditional replacement of value

    Transformation steps:
    1. Find the column containing the value 4; this acts as the axis to split the grid.
    2. Split the grid into left_half (left of the axis) and right_half (right of the axis).
    3. Add the two halves together
    4. If the sum of the two halves is 0, then output 0, else output 2
    """
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape

    # Step 1: Find the column containing the value 4s (the axis)
    col_with_4 = None
    for i in range(ncols):
        if np.array_equal(input_grid[:, i], 4 * np.ones(nrows)):
            col_with_4 = i
            break


    left_half = input_grid[:, :col_with_4]            # Step 2: Get the left half from the axis
    right_half = input_grid[:, col_with_4 + 1:]       # Step 2: Get the right half from the axis

    # Step 3: add the two halves together
    added = left_half + right_half
    # Step 4: If the sum of the two halves is 0, then output 0, else output 2
    output_grid = np.where(added == 0, 0, 2)

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_e133d23d(input_grid)
    return _result
