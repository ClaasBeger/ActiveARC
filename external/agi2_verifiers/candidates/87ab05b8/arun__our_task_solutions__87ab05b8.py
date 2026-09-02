"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 87ab05b8
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__87ab05b8
"""
from __future__ import annotations



import numpy as np

def solve_87ab05b8(input_grid):
    """
    Concepts: Grid cleaning, fill (colored) the closest corner with identified value (color)
 
    Steps:
    1. Create a blank output grid filled with 6 (Grid cleaning)
    2. Find the position of value 2.
    3. Calculate distances from this position to all four corners.
    4. Identify the closest corner.
    5. Fill a 2x2 block in that corner with value 2.
    """
    from grid_utils import group_connected_positions
 
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
   
    # Initialize output grid with all 6s
    output_grid = np.full((nrows, ncols), 6)
   
    # Find the position of value 2
    position_of_2 = np.argwhere(input_grid == 2)[0]
   
    # Define the four corners of the grid
    corners = [
        (0, 0),              # Top-left
        (0, ncols - 1),      # Top-right
        (nrows - 1, 0),      # Bottom-left
        (nrows - 1, ncols - 1)  # Bottom-right
    ]
   
    # Calculate Euclidean distances from value 2 to each corner
    distances_to_corners = []
    for corner in corners:
        distance = np.linalg.norm(np.array(corner) - position_of_2)
        distances_to_corners.append(distance)
   
    # Find the closest corner
    closest_corner_index = np.argmin(distances_to_corners)
   
    # Fill a 2x2 block in the closest corner with 2s
    if closest_corner_index == 0:  # Top-left corner
        output_grid[:2, :2] = 2
    elif closest_corner_index == 1:  # Top-right corner
        output_grid[:2, -2:] = 2
    elif closest_corner_index == 2:  # Bottom-left corner
        output_grid[-2:, :2] = 2
    elif closest_corner_index == 3:  # Bottom-right corner
        output_grid[-2:, -2:] = 2
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_87ab05b8(input_grid)
    return _result
