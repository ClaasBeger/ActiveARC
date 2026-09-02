"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 34b99a2b
source: ArunSehrawat/arc-agi2-solutions:llm
original_path: llm_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__llm_task_solutions__34b99a2b
"""
from __future__ import annotations



import numpy as np

def solve_34b99a2b(input_grid):
    """
    Concepts: symmetry, XOR gate, scalar multiplication

    Transformation steps:
    1. Identify the column of 4s that divides the grid into two equal-size parts.
    2. XOR the occupancy of the left and right parts.
    3. Multiply the result by 2.
    """
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape

    col_with_4 = None
    for i in range(ncols):
        if np.array_equal(input_grid[:, i], 4 * np.ones(nrows)):
            col_with_4 = i
            break

    left = input_grid[:, :col_with_4]
    right = input_grid[:, col_with_4 + 1:]
    output_grid = ((left != 0) ^ (right != 0)).astype(int) * 2
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_34b99a2b(input_grid)
    return _result
