"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 14b8e18c
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__14b8e18c
"""
from __future__ import annotations



import numpy as np

def solve_14b8e18c(input_grid):
    """
    Concepts:
    - Identify square compartments formed by non-background values.
    - For each square compartment, mark its corners with value 2.
   
    Steps:
    1. Find the non-background value (value different from 7).
    2. Group connected positions containing this value.
    3. For each group:
        - Determine if it forms a square compartment.
        - If it's a square with consistent border values, mark its corners with 2.
    """
    from grid_utils import group_connected_positions
 
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()
 
    # Find the non-background value (value that is not 7)
    non_background_val = np.unique(input_grid[input_grid != 7])[0]
   
    # Find and group connected positions of non-background values
    positions_non_background = np.argwhere(input_grid == non_background_val)
    connected_groups = group_connected_positions(positions_non_background)
 
    # Process each connected group (potential compartment)
    for group in connected_groups:
        group = np.array(group)
        min_row, min_col = group.min(axis=0)
        max_row, max_col = group.max(axis=0)
        height, width = max_row - min_row + 1, max_col - min_col + 1
 
        # Extract frame values (border of the compartment)
        frame = []
        frame.extend(input_grid[min_row, min_col:max_col+1])  # Top row
        frame.extend(input_grid[max_row, min_col:max_col+1])  # Bottom row
        frame.extend(input_grid[min_row:max_row+1, min_col])  # Left column
        frame.extend(input_grid[min_row:max_row+1, max_col])  # Right column
 
        # Define corner positions around the compartment
        corner_positions = [
            (min_row, min_col-1), (min_row-1, min_col),       # Top-left corners
            (min_row, max_col+1), (min_row-1, max_col),       # Top-right corners
            (max_row+1, min_col), (max_row, min_col-1),       # Bottom-left corners
            (max_row+1, max_col), (max_row, max_col+1)        # Bottom-right corners
        ]
       
        # Check if it's a square compartment with consistent border
        if height == width and all(val == non_background_val for val in frame):
            # Mark all valid corner positions with value 2
            for r, c in corner_positions:
                if 0 <= r < nrows and 0 <= c < ncols:
                    output_grid[r, c] = 2
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_14b8e18c(input_grid)
    return _result
