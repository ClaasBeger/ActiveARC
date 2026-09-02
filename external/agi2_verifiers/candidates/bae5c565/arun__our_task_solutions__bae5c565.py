"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: bae5c565
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__bae5c565
"""
from __future__ import annotations



import numpy as np

def solve_bae5c565(input_grid):
    """
    Concepts: The Galton board — filling columns based on a reference row and a pivot point.

    Transformation steps:
    1. Identify a pivot column using the value 8 in the bottom row
    2. Count the number of 8s in the pivot column to determine fill depth
    3. Use the top row as a reference for values (colors) to fill into columns
    4. Fill values from the bottom up based on distance from pivot
    5. Replace the top reference row with background value 5
    """

    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()

    # Find the column with value 8 in the bottom row as pivot point
    pos_with_8 = np.argwhere(input_grid[-1] == 8)[0][0]
    col_with_8 = input_grid[:, pos_with_8]
    num_8s = np.sum(col_with_8 == 8)
    
    # Use the top row as the reference for column values
    top_row = input_grid[0]
    
    # Fill columns to the left of pivot
    for c, val in enumerate(top_row[:pos_with_8]):
        # Calculate fill height based on column distance from pivot
        fill_height = c + (num_8s - pos_with_8)
        # Fill from bottom up
        output_grid[-fill_height:, c] = val
    
    # Fill columns to the right of pivot
    for c, val in enumerate(top_row[pos_with_8+1:]):
        # Calculate fill height based on column distance from pivot
        fill_height = num_8s - 1 - c
        # Fill from bottom up
        output_grid[-fill_height:, c + pos_with_8 + 1] = val

    # Replace the reference row with background value 5
    output_grid[0] = 5

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_bae5c565(input_grid)
    return _result
