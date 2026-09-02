"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 72a961c9
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__72a961c9
"""
from __future__ import annotations



import numpy as np

def solve_72a961c9(input_grid):
    """
    Concepts: Build columns (towers) of different heights above certain values (2 and 8).

    Transformation steps:
    1. Identify all positions of the value 8 in the input grid.
       - Replace the two rows above each position with 1s.
       - Set the value at three rows above to 8.
    2. Identify all positions of the value 2 in the input grid.
       - Replace the three rows above each position with 1s.
       - Set the value at four rows above to 2.
    """

    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()

    # Process positions with value 8
    pos_with_8 = np.argwhere(input_grid == 8)
    for r, c in pos_with_8:
        output_grid[r-2:r, c] = 1
        output_grid[r-3, c] = 8

    # Process positions with value 2
    pos_with_2 = np.argwhere(input_grid == 2)
    for r, c in pos_with_2:
        output_grid[r-3:r, c] = 1
        output_grid[r-4, c] = 2

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_72a961c9(input_grid)
    return _result
