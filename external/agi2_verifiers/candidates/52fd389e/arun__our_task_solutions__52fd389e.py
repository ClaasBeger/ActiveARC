"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 52fd389e
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__52fd389e
"""
from __future__ import annotations



import numpy as np

def solve_52fd389e(input_grid):
    """
    Concepts: Frame (pad) every non-zero block with value (color) and thickness illustrated in the block.
 
    Steps:
    1. Find and group connected non-zero positions.
    2. For each group:
        - Extract the block defined by the group.
        - Find non-4 elements and their value.
        - Add a frame around the block with thickness equal to the count of non-4 elements.
        - Place the framed block back into the output grid.
    """
    from grid_utils import group_connected_positions
 
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()
 
    # Find and group non-zero positions
    non_zero_positions = np.argwhere(input_grid != 0)
    connected_groups = group_connected_positions(non_zero_positions)
 
    # Process each connected group
    for group in connected_groups:
        group = np.array(group)
        min_row, min_col = group.min(axis=0)
        max_row, max_col = group.max(axis=0)
       
        # Extract the block defined by this group
        block = input_grid[min_row:max_row+1, min_col:max_col+1]
 
        # Find non-4 elements and their value
        non_4_positions = np.argwhere(block != 4)
       
        # Skip if there are no non-4 elements or multiple values
        if len(non_4_positions) == 0:
            continue
           
        # Get the unique non-4 value (assuming all non-4 elements have the same value)
        frame_value = np.unique(block[non_4_positions[:, 0], non_4_positions[:, 1]])[0]
        frame_thickness = len(non_4_positions)
       
        # Add a frame around the block with thickness equal to count of non-4 elements
        if frame_thickness > 0:
            framed_block = np.pad(
                block,
                pad_width=frame_thickness,
                mode='constant',
                constant_values=frame_value
            )
           
            # Place the framed block back into the output grid
            r_start = max(0, min_row - frame_thickness)
            r_end = min(nrows, max_row + 1 + frame_thickness)
            c_start = max(0, min_col - frame_thickness)
            c_end = min(ncols, max_col + 1 + frame_thickness)
           
            # Adjust framed block if it would go out of bounds
            fr_start = max(0, frame_thickness - min_row)
            fr_end = framed_block.shape[0] - max(0, (max_row + 1 + frame_thickness) - nrows)
            fc_start = max(0, frame_thickness - min_col)
            fc_end = framed_block.shape[1] - max(0, (max_col + 1 + frame_thickness) - ncols)
           
            output_grid[r_start:r_end, c_start:c_end] = framed_block[fr_start:fr_end, fc_start:fc_end]
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_52fd389e(input_grid)
    return _result
