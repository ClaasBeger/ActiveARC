"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9841fdad
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__9841fdad
"""
from __future__ import annotations



import numpy as np

def solve_9841fdad(input_grid):
    """
    Concepts:
    - Identify columns with unique values that act as separators.
    - Extract a reference block and a placeholder block separated by these columns.
    - Find patterns in the reference block and apply corresponding transformations
      to the placeholder block based on their positions and dimensions.
 
    Steps:
    1. Find columns with unique values (separators).
    2. Extract reference block and placeholder block.
    3. Find connected components of non-1 values in the reference block.
    4. For each component:
        - If it's a square:
            - If near left boundary, copy it to left side of placeholder block.
            - If near right boundary, copy it to right side of placeholder block.
        - If it's wider than tall, extend it across the placeholder block with same height.
    5. Update the output grid with the modified placeholder block.
    """
    from grid_utils import group_connected_positions
 
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()
 
    # Find columns with unique values (separators)
    separator_columns = []
    for col in range(ncols):
        unique_values = set(input_grid[:, col])
        if len(unique_values) == 1:
            separator_columns.append(col)
 
    # Extract reference and placeholder blocks
    reference_block = input_grid[1:nrows-1, 1:separator_columns[1]]
    placeholder_block = input_grid[1:nrows-1, separator_columns[1]+1:ncols-1]
 
    # Find connected components of non-1 values in reference block
    non_1_positions = np.argwhere(reference_block != 1)
    non_1_components = group_connected_positions(non_1_positions)
   
    # Process each component
    for component in non_1_components:
        component = np.array(component)
        min_row, min_col = component.min(axis=0)
        max_row, max_col = component.max(axis=0)
       
        # Get the value of this component (assuming uniform value)
        component_value = np.unique(reference_block[min_row:max_row+1, min_col:max_col+1])[0]
       
        # Calculate height and width
        height = max_row - min_row + 1
        width = max_col - min_col + 1
       
        # Apply transformations based on component shape and position
        if height == width:  # Square component
            if min_col == 1:  # Near left boundary
                # Copy square to left side of placeholder block for each row in component
                for row in np.unique(component[:, 0]):
                    placeholder_block[row, 1:height+1] = component_value
           
            elif max_col == reference_block.shape[1]-2:  # Near right boundary
                # Copy square to right side of placeholder block for each row in component
                for row in np.unique(component[:, 0]):
                    placeholder_block[row, -height-1:-1] = component_value
       
        elif height < width:  # Rectangle wider than tall
            # Extend horizontally across placeholder block for each row in component
            placeholder_width = placeholder_block.shape[1]-2
            for row in np.unique(component[:, 0]):
                placeholder_block[row, 1:placeholder_width+1] = component_value
 
    # Update output grid with modified placeholder block
    output_grid[1:nrows-1, separator_columns[1]+1:ncols-1] = placeholder_block
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_9841fdad(input_grid)
    return _result
