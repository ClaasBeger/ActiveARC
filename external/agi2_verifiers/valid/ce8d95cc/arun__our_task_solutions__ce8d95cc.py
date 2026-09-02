"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ce8d95cc
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__ce8d95cc
"""
from __future__ import annotations



import numpy as np

def solve_ce8d95cc(input_grid):
    """
    Concepts: Grid compression by collapsing consecutive identical rows/columns.

    Transformation steps:
    1. Remove duplicate consecutive rows.
    2. Remove duplicate consecutive columns.
    """

    input_grid = np.array(input_grid)

    # Step 1: remove consecutive duplicate rows
    mask_rows = np.any(input_grid[1:] != input_grid[:-1], axis=1)
    keep_rows = np.r_[True, mask_rows]
    reduced = input_grid[keep_rows]

    # Step 2: remove consecutive duplicate columns
    mask_cols = np.any(reduced[:, 1:] != reduced[:, :-1], axis=0)
    keep_cols = np.r_[True, mask_cols]
    output_grid = reduced[:, keep_cols]

    # Alternative approach: using a loop to remove duplicates
    # for r in range(output_grid.shape[0] - 1):
    #     if np.array_equal(output_grid[r], output_grid[r + 1]):
    #         output_grid = np.delete(output_grid, r, axis=0)

    # for c in range(output_grid.shape[1] - 1):
    #     if np.array_equal(output_grid[:, c], output_grid[:, c + 1]):
    #         output_grid = np.delete(output_grid, c, axis=1)

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_ce8d95cc(input_grid)
    return _result
