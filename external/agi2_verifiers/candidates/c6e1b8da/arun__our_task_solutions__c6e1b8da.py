"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: c6e1b8da
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__c6e1b8da
"""
from __future__ import annotations



import numpy as np

def solve_c6e1b8da(input_grid):
    """
    Transform shapes by moving rectangles to stick ends and filling gaps.
    
    Concepts:
    - Connected component analysis
    - Rectangle detection and extraction
    - Directional movement based on stick position
    - Gap filling in transformed shapes
    
    Transformation steps:
    1. Find all non-zero connected components (they will be overlapping rectangles with and without sticks)
    2. For each component:
        a. Extract bounding box
        b. If contains gaps (stick), identify stick direction
        c. Move rectangle part to stick end
    3. Fill any occurred gaps in the rectangles in output

    """
    from grid_utils import group_connected_positions

    def move_rectangle(block, direction, dimensions):
        """Helper to extract and position rectangle based on stick direction."""
        H, W = dimensions
        if direction == "bottom":
            return block[0:min_r, :], H - min_r
        elif direction == "right":
            return block[:, 0:min_c], W - min_c
        elif direction == "top":
            return block[max_r+1:, :], 0
        else:  # left
            return block[:, max_c+1:], 0

    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()
    
    # Process each non-zero value
    for val in np.unique(input_grid[input_grid != 0]):
        positions = np.argwhere(input_grid == val)
        components = group_connected_positions(positions)
        
        # Handle each connected component
        for component in components:
            component = np.array(component)
            min_row, min_col = component.min(axis=0)
            max_row, max_col = component.max(axis=0)
            height, width = max_row - min_row + 1, max_col - min_col + 1
            
            block = input_grid[min_row:max_row + 1, min_col:max_col + 1]
            if not np.any(block == 0):
                continue
                
            # Clear original component
            output_grid[component[:, 0], component[:, 1]] = 0
            
            # Find stick position
            non_val_pos = np.argwhere(block != val)
            min_r, min_c = non_val_pos.min(axis=0)
            max_r, max_c = non_val_pos.max(axis=0)
            
            # Determine stick direction and move rectangle
            if min_r != 0: # stick is along a row till the bottom of the block
                direction = "bottom"
            elif min_c != 0: # stick is along a column till the right boundary of the block
                direction = "right"
            elif max_r != height - 1: # stick is along a row till the top of the block
                direction = "top"
            else: # stick is along a column till the left boundary of the block
                direction = "left"
                
            rectangle, shift = move_rectangle(block, direction, (height, width))
            
            # Place rectangle in new position
            if direction in ["bottom", "top"]:
                output_grid[min_row + shift:min_row + shift + rectangle.shape[0], 
                          min_col:min_col + rectangle.shape[1]] = rectangle
            else:
                output_grid[min_row:min_row + rectangle.shape[0],
                          min_col + shift:min_col + shift + rectangle.shape[1]] = rectangle

    # if any gap occures in the rectangles in output, fill them
    for val in np.unique(output_grid[output_grid != 0]):
        positions = np.argwhere(output_grid == val)
        components = group_connected_positions(positions)
        for component in components:
            component = np.array(component)
            min_row, min_col = component.min(axis=0)
            max_row, max_col = component.max(axis=0)
            block = output_grid[min_row:max_row + 1, min_col:max_col + 1]
            block[block == 0] = val
            output_grid[min_row:max_row + 1, min_col:max_col + 1] = block

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_c6e1b8da(input_grid)
    return _result
