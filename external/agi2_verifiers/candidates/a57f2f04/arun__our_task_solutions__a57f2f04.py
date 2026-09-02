"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: a57f2f04
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__a57f2f04
"""
from __future__ import annotations



import numpy as np

def solve_a57f2f04(input_grid):
    """
    Concepts:
    - Identify blocks in the grid (areas not containing value 8).
    - Extract the smallest meaningful sub-pattern within each block.
    - Repeat this sub-pattern to fill the entire block.
 
    Steps:
    2. Find and group connected non-8 positions in the grid
    3. For each group:
        - Extract the block defined by the group.
        - Find the smallest sub-pattern (non-zero elements) within the block.
        - Tile the sub-pattern to fill the entire block.
    """
    from grid_utils import group_connected_positions
 
    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()
 
    # Find and group non-8 positions
    non_8_positions = np.argwhere(input_grid != 8)
    connected_non_8_groups = group_connected_positions(non_8_positions)
   
    # Process each connected group
    for group in connected_non_8_groups:
        group = np.array(group)
        min_row, min_col = group.min(axis=0)
        max_row, max_col = group.max(axis=0)
       
        # Extract the block defined by this group
        block = input_grid[min_row:max_row+1, min_col:max_col+1]
       
        # Find the smallest sub-pattern (non-zero elements)
        non_zero_positions = np.argwhere(block != 0)
        if len(non_zero_positions) == 0:
            continue  # Skip empty blocks
           
        min_sub_row, min_sub_col = non_zero_positions.min(axis=0)
        max_sub_row, max_sub_col = non_zero_positions.max(axis=0)
        sub_pattern = block[min_sub_row:max_sub_row+1, min_sub_col:max_sub_col+1]
       
        # Calculate number of repetitions needed
        pattern_height, pattern_width = sub_pattern.shape
        vertical_repeats = block.shape[0] // pattern_height
        horizontal_repeats = block.shape[1] // pattern_width
       
        # Tile the sub-pattern to fill the block
        for r in range(vertical_repeats):
            for c in range(horizontal_repeats):
                row_start = r * pattern_height
                row_end = (r + 1) * pattern_height
                col_start = c * pattern_width
                col_end = (c + 1) * pattern_width
                block[row_start:row_end, col_start:col_end] = sub_pattern
       
        # Update the output grid with the filled block
        output_grid[min_row:max_row+1, min_col:max_col+1] = block
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_a57f2f04(input_grid)
    return _result
