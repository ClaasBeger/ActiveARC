"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: b25e450b
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__b25e450b
"""
from __future__ import annotations



import numpy as np

def solve_b25e450b(input_grid):
    """
    Clears grass (color 5) in rows/columns based on grass cutters (color 0) at the edges,
    then repositions the grass cutters at the opposite edges.
   
    Concept:
    When a grass cutter (value 0) is placed at an edge of the grid, it clears all grass in
    the corresponding row or column and then moves to the opposite edge.
   
    Transformation Steps:
    1. Identify grass cutters (color 0) at the edges of the grid
    2. For each grass cutter:
       a. If at top/bottom edge, clear the entire column (replace with background color)
       b. If at left/right edge, clear the entire row (replace with background color)
    3. Reposition each grass cutter to the opposite edge:
       a. From top → bottom, bottom → top
       b. From left → right, right → left
    """
    from grid_utils import group_connected_positions
 
 
    # Convert input to numpy array if it's not already
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()
 
    # Define the background color (represents cleared grass)
    background_color = 7
     
    # Find all grass cutter positions (value 0)
    grass_cutter_positions = np.argwhere(input_grid == 0)
   
    # If there are no grass cutters, return the original grid
    if len(grass_cutter_positions) == 0:
        return output_grid
   
    # Group connected grass cutter positions
    grass_cutter_groups = group_connected_positions(grass_cutter_positions)
   
    # First pass: Clear grass in rows/columns based on grass cutter positions
    for cutter_group in grass_cutter_groups:
        cutter_group = np.array(cutter_group)
        min_row, min_col = cutter_group.min(axis=0)
        max_row, max_col = cutter_group.max(axis=0)
        height = max_row - min_row + 1
        width = max_col - min_col + 1
       
        # Check grass cutter position and clear corresponding row/column
        if min_row == 0:  # Grass cutter at the top edge
            output_grid[:, min_col:max_col+1] = background_color  # Clear the entire column
        elif max_row == nrows - 1:  # Grass cutter at the bottom edge
            output_grid[:, min_col:max_col+1] = background_color  # Clear the entire column
        elif min_col == 0:  # Grass cutter at the left edge
            output_grid[min_row:max_row+1, :] = background_color  # Clear the entire row
        elif max_col == ncols - 1:  # Grass cutter at the right edge
            output_grid[min_row:max_row+1, :] = background_color  # Clear the entire row
 
    # Second pass: Reposition grass cutters to opposite edges
    for cutter_group in grass_cutter_groups:
        cutter_group = np.array(cutter_group)
        min_row, min_col = cutter_group.min(axis=0)
        max_row, max_col = cutter_group.max(axis=0)
        height = max_row - min_row + 1
        width = max_col - min_col + 1
       
        # Reposition grass cutters based on their original position
        if min_row == 0:  # Grass cutter was at the top edge
            output_grid[-height:, min_col:max_col+1] = 0  # Move to the bottom edge
        elif max_row == nrows - 1:  # Grass cutter was at the bottom edge
            output_grid[:height, min_col:max_col+1] = 0  # Move to the top edge
        elif min_col == 0:  # Grass cutter was at the left edge
            output_grid[min_row:max_row+1, -width:] = 0  # Move to the right edge
        elif max_col == ncols - 1:  # Grass cutter was at the right edge
            output_grid[min_row:max_row+1, :width] = 0  # Move to the left edge
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_b25e450b(input_grid)
    return _result
