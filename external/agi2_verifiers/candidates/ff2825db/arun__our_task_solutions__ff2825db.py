"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ff2825db
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__ff2825db
"""
from __future__ import annotations



import numpy as np

def solve_ff2825db(input_grid):
    """
    Draws two frames using the most frequent nonzero value in the interior of the grid:
    - An inner frame around the bounding box of the most frequent value in the interior.
    - An outer frame (excluding the first row) using the same value.

    Concepts:
    - Frequency analysis in a subgrid
    - Bounding box detection
    - Frame drawing

    Transformation Steps:
    1. Extract the interior (excluding first two rows and first/last columns).
    2. Find the most frequent nonzero value in the interior.
    3. Find the bounding box of this value in the interior.
    4. Clear the interior region totally.
    5. Draw an inner frame around the bounding box using the detected value.
    6. Draw an outer frame (excluding the first row) using the same value.
    """
    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()

    # Extract interior (excluding first two rows and first/last columns)
    interior = input_grid[2:-1, 1:-1]

    # Find most frequent nonzero value in the interior
    unique, count = np.unique(interior[interior != 0], return_counts=True)
    if len(unique) == 0:
        return output_grid  # No nonzero values to frame

    most_freq_val = unique[np.argmax(count)]

    # Find bounding box of the most frequent value
    pos_with_most_freq = np.argwhere(interior == most_freq_val)
    min_row, min_col = pos_with_most_freq.min(axis=0)
    max_row, max_col = pos_with_most_freq.max(axis=0)

    # Clear interior
    output_grid[2:-1, 1:-1] = 0

    # Draw inner frame
    row_offset, col_offset = 2, 1
    output_grid[min_row + row_offset, min_col + col_offset : max_col + col_offset + 1] = most_freq_val
    output_grid[max_row + row_offset, min_col + col_offset : max_col + col_offset + 1] = most_freq_val
    output_grid[min_row + row_offset : max_row + row_offset + 1, min_col + col_offset] = most_freq_val
    output_grid[min_row + row_offset : max_row + row_offset + 1, max_col + col_offset] = most_freq_val

    # Draw outer frame (excluding first row)
    output_grid[1] = most_freq_val
    output_grid[-1] = most_freq_val
    output_grid[1:-1, 0] = most_freq_val
    output_grid[1:-1, -1] = most_freq_val

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_ff2825db(input_grid)
    return _result
