"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 305b1341
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__305b1341
"""
from __future__ import annotations



import numpy as np

def solve_305b1341(input_grid):
    """
    Concepts: Value mapping and neighborhood transformation.

    Transformation steps:
    1. Identify unique values in the grid that appear more than once, excluding zeros.
    2. Extract a mapping grid from top-left corner of the input grid.
    3. Replace values in the neighboring cells based on the mapping.
    """
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()

    # Step 1: Identify unique values with counts greater than 1, excluding zeros
    unique, counts = np.unique(input_grid, return_counts=True)
    unique_vals = unique[counts > 1]
    unique_vals = unique_vals[unique_vals != 0]

    # Step 2: Extract a mapping grid from top-left corner of the input grid
    num_unique_vals = len(unique_vals)
    map_grid = input_grid[:num_unique_vals, :2]

    # Clear the mapping region in the output grid
    output_grid[:num_unique_vals, :2] = 0
    input_without_map = input_grid.copy()
    input_without_map[:num_unique_vals, :2] = 0

    # Step 3: Replace values in the neighboring cells based on the mapping.
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for i in range(num_unique_vals):
        val_to_replace = map_grid[i, 0]
        replacement_val = map_grid[i, 1]
        positions = np.argwhere(input_without_map == val_to_replace)

        for pos in positions:
            r, c = pos[0], pos[1]
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < nrows and 0 <= nc < ncols:
                    if output_grid[nr, nc] == 0:
                        output_grid[nr, nc] = replacement_val

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_305b1341(input_grid)
    return _result
