"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 22208ba4
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__22208ba4
"""
from __future__ import annotations



import numpy as np

def solve_22208ba4(input_grid):
    """
    From the corners, select the blocks of the same color that occurs the most.
    Moves the colored blocks from their corner positions toward opposite corners.
 
    Concept:
        - Identify the background color as the most frequent color.
        - Among non-background colors, select the one with the highest number of connected groups.
        - For each connected group of that color, erase it from its original position and move the block toward the opposite corner.
 
    Steps:
        1. Determine background color and non-background colors.
        2. Find the non-background color with the most connected groups.
        3. For each group of that color, erase the block and place it in the opposite corner if it fits.
    """
    import numpy as np
    from grid_utils import group_connected_positions
 
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = np.copy(input_grid)
 
    # Identify background color (most frequent)
    unique_colors, counts = np.unique(input_grid, return_counts=True)
    order = np.argsort(-counts)  # descending order
    background_color = unique_colors[order[0]]
    non_bg_colors = unique_colors[order[1:]]
   
    # Select the blocks of the same color that occurs the most.
    selected_groups = None
    max_num_groups = 0
    for color in non_bg_colors:
        positions = np.argwhere(input_grid == color)
        groups = group_connected_positions(positions)
        num_groups = len(groups)
        if num_groups > max_num_groups:
            max_num_groups = num_groups
            selected_color = color
            selected_groups = groups
 
    if selected_groups is not None:
        for group in selected_groups:
            group = np.array(group)
            min_row, min_col = group.min(axis=0)
            max_row, max_col = group.max(axis=0)
            output_grid[min_row:max_row+1, min_col:max_col+1] = background_color
            block = input_grid[min_row:max_row+1, min_col:max_col+1]
            H, W = block.shape
 
            # Move the selected block to the appropriate corner
            if min_row == 0 and min_col == 0:  # move block toward bottom-right
                new_min_row = min_row + H
                new_min_col = min_col + W
                output_grid[new_min_row:new_min_row+H, new_min_col:new_min_col+W] = block
            elif min_row == 0 and max_col == ncols - 1:  # move block toward bottom-left
                new_min_row = min_row + H
                new_max_col = max_col - W
                output_grid[new_min_row:new_min_row+H, new_max_col-W+1:new_max_col+1] = block
            elif max_row == nrows - 1 and min_col == 0:  # move block toward top-right
                new_max_row = max_row - H
                new_min_col = min_col + W
                output_grid[new_max_row-H+1:new_max_row+1, new_min_col:new_min_col+W] = block
            elif max_row == nrows - 1 and max_col == ncols - 1:  # move block toward top-left
                new_max_row = max_row - H
                new_max_col = max_col - W
                output_grid[new_max_row-H+1:new_max_row+1, new_max_col-W+1:new_max_col+1] = block
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_22208ba4(input_grid)
    return _result
