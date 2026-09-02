"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: fc754716
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__fc754716
"""
from __future__ import annotations



import numpy as np

def solve_fc754716(input_grid):
    """
    Find center color (value) in the input grid and create a frame around it of the same color.
    
    Concepts:
    - Center identification: Locating the center cell of a grid
    - Value extraction: Retrieving the color/value from the center position
    - Frame creation: Using the extracted value to create a border around the entire grid
    - Value replacement: Setting the center position to 0 (background)
    
    Transformation Steps:
    1. Extract the value from the center cell of the input grid
    2. Replace the center cell value with 0
    3. Create a frame/border around the entire grid using the center value
    """
    
    # Convert to numpy array
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()

    # Extract the center value
    central_val = input_grid[nrows//2, ncols//2]
    
    # Replace center value with 0
    output_grid[nrows//2, ncols//2] = 0

    # Create a frame around the grid using the central value
    output_grid[0, :] = central_val    # Top row
    output_grid[-1, :] = central_val   # Bottom row
    output_grid[:, 0] = central_val    # Left column
    output_grid[:, -1] = central_val   # Right column

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_fc754716(input_grid)
    return _result
