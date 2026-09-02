"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 19bb5feb
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__19bb5feb
"""
from __future__ import annotations



import numpy as np

def solve_19bb5feb(input_grid):
    """
    Concepts: Bounding box detection, Subgrid extraction, Unique value identification, 
    Anchor-based positioning, Canonical mapping (normalization to 2×2 grid

    Transformation steps:
    1. Find the bounding box of all cells with value 8.
    2. Extract the block within this bounding box.
    3. Identify all unique values in the block that are not 8.
    4. For each unique value, find its top-left position in the block.
    5. Place each value in the corresponding corner of a 2x2 output grid:
       - Top-left, Top-right, Bottom-left, Bottom-right.
    """

    input_grid = np.array(input_grid)

    # Step 1: Find the bounding box of all cells with value 8.
    pos_with_8 = np.argwhere(input_grid == 8)
    min_row, min_col = pos_with_8.min(axis=0)
    max_row, max_col = pos_with_8.max(axis=0)
    # Step 2: Extract the block within this bounding box.
    block = input_grid[min_row:max_row + 1, min_col:max_col + 1]

    # Step 3: Identify all unique values in the block that are not 8.
    unique_vals = np.unique(block[block != 8])

    # Step 4: For each unique value, find its top-left position in the block.
    corners = []
    for val in unique_vals:
        pos = np.argwhere(block == val)
        min_r, min_c = pos.min(axis=0)
        corners.append([min_r, min_c])
    corners = np.array(corners)

    # Step 5: Place each value in the corresponding corner of a 2x2 output grid.
    output_grid = np.zeros((2, 2), dtype=int)
    min_r, min_c = corners.min(axis=0)
    max_r, max_c = corners.max(axis=0)
    for i, (r, c) in enumerate(corners):
        if r == min_r and c == min_c:
            output_grid[0, 0] = unique_vals[i]
        if r == min_r and c == max_c:
            output_grid[0, 1] = unique_vals[i]
        if r == max_r and c == min_c:
            output_grid[1, 0] = unique_vals[i]
        if r == max_r and c == max_c:
            output_grid[1, 1] = unique_vals[i]

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_19bb5feb(input_grid)
    return _result
