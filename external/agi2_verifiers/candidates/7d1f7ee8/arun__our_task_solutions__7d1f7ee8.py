"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 7d1f7ee8
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__7d1f7ee8
"""
from __future__ import annotations



import numpy as np

def solve_7d1f7ee8(input_grid):
    """
    Concept:
    Color nested rectangles with the color of their containing rectangle.
   
    Steps:
    1. Identify all rectangles in the grid by their outlines.
    2. Create a copy of the grid and remove interior of all rectangles.
    3. Find the outermost rectangles that remain after this process.
    4. For each outermost rectangle, color all interior rectangles with its color.
    5. Return the modified grid with colored nested rectangles.
    """
    from grid_utils import group_connected_positions
 
    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()
   
    # Create a working copy to identify outermost rectangles
    working_grid = input_grid.copy()
 
    # Find all unique non-zero values (rectangle colors)
    unique_values = np.unique(input_grid[input_grid != 0])
   
    # First pass: hollow out all rectangles to identify nested structures
    for value in unique_values:
        # Find positions of the current value
        value_positions = np.argwhere(input_grid == value)
       
        # Group connected positions into separate rectangles
        rectangle_groups = group_connected_positions(value_positions)
       
        # Process each rectangle
        for rectangle in rectangle_groups:
            rectangle = np.array(rectangle)
           
            # Find rectangle boundaries
            min_row, min_col = rectangle.min(axis=0)
            max_row, max_col = rectangle.max(axis=0)
           
            # Remove the interior (hollow out the rectangle)
            # This helps identify which rectangles are outermost
            working_grid[min_row+1:max_row, min_col+1:max_col] = 0
 
    # Find remaining values in the working grid (these are outermost rectangles)
    outermost_rectangle_values = np.unique(working_grid[working_grid != 0])
 
    # Second pass: color interior rectangles with the color of their container
    for value in outermost_rectangle_values:
        # Find positions of the current outermost rectangle
        value_positions = np.argwhere(working_grid == value)
           
        # Find outermost rectangle boundaries
        min_row, min_col = value_positions.min(axis=0)
        max_row, max_col = value_positions.max(axis=0)
       
        # Extract the interior region from the output grid
        interior_region = output_grid[min_row+1:max_row, min_col+1:max_col]
       
        # Find non-zero positions in the interior (these are nested rectangles)
        non_zero_interior = np.argwhere(interior_region != 0)
       
        # Color these positions with the value of the outermost rectangle
        if non_zero_interior.size > 0:
            interior_region[non_zero_interior[:, 0], non_zero_interior[:, 1]] = value
           
        # Update the output grid with the modified interior
        output_grid[min_row+1:max_row, min_col+1:max_col] = interior_region
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_7d1f7ee8(input_grid)
    return _result
