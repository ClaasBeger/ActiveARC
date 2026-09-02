"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 79cce52d
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__79cce52d
"""
from __future__ import annotations



import numpy as np

def solve_79cce52d(input_grid):
    """
    Concepts:
    - Use value 2 at the top and left edges as position markers.
    - Divide the grid into four quadrants based on these markers.
    - Rearrange the quadrants by rotating them to create the output_grid
 
    Steps:
    1. Remove the first row and column (border).
    2. Find the positions of markers (value 2) to determine quadrant sizes.
    3. Split the grid into four quadrants.
    4. Rearrange the quadrants in a new configuration.
    5. Return the rearranged grid.
    """
 
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
   
    # Remove border (first row and column)
    inner_grid = input_grid[1:, 1:]
   
    # Find marker positions (value 2) to determine quadrant boundaries
    # Calculate from the end of grid to get quadrant heights/widths
    quadrant_height = nrows - np.argwhere(input_grid[:, 0] == 2)[0][0]
    quadrant_width = ncols - np.argwhere(input_grid[0, :] == 2)[0][0]
   
    # Split the grid into four quadrants
    top_left = inner_grid[:quadrant_height, :quadrant_width]
    top_right = inner_grid[:quadrant_height, quadrant_width:]
    bottom_left = inner_grid[quadrant_height:, :quadrant_width]
    bottom_right = inner_grid[quadrant_height:, quadrant_width:]
   
    # Rearrange the quadrants (rotate them)
    # Create new grid with: [bottom_right, bottom_left] on top and [top_right, top_left] on bottom
    output_grid = np.vstack((
        np.hstack((bottom_right, bottom_left)),
        np.hstack((top_right, top_left))
    ))
   
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_79cce52d(input_grid)
    return _result
