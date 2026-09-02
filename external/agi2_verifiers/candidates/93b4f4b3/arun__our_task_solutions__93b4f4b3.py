"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 93b4f4b3
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__93b4f4b3
"""
from __future__ import annotations



import numpy as np

def solve_93b4f4b3(input_grid):
    """
    Concepts: Connected component matching based on their shapes.
    
    Fill the color (value) in the left part based from the right part by matching shapes.

    Transformation steps:
    2. Split the grid into left and right parts.
    3. Extract connected components from the right part with their values and normalize their positions.
    4. Match shapes and transfer values from the right part to corresponding empty spaces in the left part.
    """
    from grid_utils import group_connected_positions

    # Convert input to a NumPy array
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape


    # Step 1: Split the grid into left and right parts
    left_part = input_grid[:, :ncols // 2]
    right_part = input_grid[:, ncols // 2:]

    # Initialize the output grid as a copy of the left part
    output_grid = left_part.copy()

    # Step 2: Extract unique non-background (non-zero) values from the right part
    unique_vals = np.unique(right_part[right_part != 0])

    # Step 2: Normalize positions of connected components in the right part
    positions_in_right = []
    for val in unique_vals:
        pos = np.argwhere(right_part == val)
        min_row, min_col = pos[:, 0].min(), pos[:, 1].min()
        pos_norm = pos - np.array([min_row, min_col])
        positions_in_right.append(pos_norm)

    # Find empty spaces (with 0s) in the left part
    empty_positions = np.argwhere(left_part == 0)
    empty_parts = group_connected_positions(empty_positions, connectivity=8)

    # Step 3: Match shapes and transfer values from the right part to the left part
    for empty_part in empty_parts:
        empty_part = np.array(empty_part)
        min_row, min_col = empty_part[:, 0].min(), empty_part[:, 1].min()
        empty_norm = empty_part - np.array([min_row, min_col])

        for val, pos_norm in zip(unique_vals, positions_in_right):
            if set(map(tuple, pos_norm)) == set(map(tuple, empty_norm)):
                for r, c in empty_part:
                    output_grid[r, c] = val

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_93b4f4b3(input_grid)
    return _result
