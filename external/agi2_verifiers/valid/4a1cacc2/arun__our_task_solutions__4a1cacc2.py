"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 4a1cacc2
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__4a1cacc2
"""
from __future__ import annotations



import numpy as np

def solve_4a1cacc2(input_grid):
    """
    Concept:
    Identify the non-8  (non-background) value in the grid and extend it from its position to the closest corner,
    filling a rectangular region.
   
    Steps:
    1. Find the unique non-8 (non-background) value in the grid.
    2. Locate the position of this value.
    3. Determine which corner is closest to this position.
    4. Fill a rectangular region from the value's position to the closest corner with this value.
    5. Return the modified grid.
    """
 
    # Convert input to numpy array
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()
 
    # Find the unique non-8 value (assumes there's only one such value)
    non_8_value = np.unique(input_grid[input_grid != 8])[0]
 
    # Find the position of the non-8 value (assumes it appears at only one position)
    non_8_position = np.argwhere(input_grid == non_8_value)[0]
    row, col = tuple(non_8_position)
 
    # Define the four corners of the grid
    corners = [
        (0, 0),              # Top-left
        (0, ncols - 1),      # Top-right
        (nrows - 1, 0),      # Bottom-left
        (nrows - 1, ncols - 1)  # Bottom-right
    ]
   
    # Calculate Euclidean distances from the non-8 value to each corner
    distances_to_corners = [np.linalg.norm(np.array(corner) - non_8_position) for corner in corners]
 
    # Find the closest corner
    closest_corner_index = np.argmin(distances_to_corners)
   
    # Fill the rectangular region from the non-8 value position to the closest corner
    if closest_corner_index == 0:  # Top-left corner
        output_grid[:row+1, :col+1] = non_8_value
    elif closest_corner_index == 1:  # Top-right corner
        output_grid[:row+1, col:] = non_8_value
    elif closest_corner_index == 2:  # Bottom-left corner
        output_grid[row:, :col+1] = non_8_value
    elif closest_corner_index == 3:  # Bottom-right corner
        output_grid[row:, col:] = non_8_value
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_4a1cacc2(input_grid)
    return _result
