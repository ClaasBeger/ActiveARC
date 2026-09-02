"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 7d7772cc
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__7d7772cc
"""
from __future__ import annotations



import numpy as np

def solve_7d7772cc(input_grid):
    """
    Detects a bracket-shaped frame (any 90° rotation) extending fully along the grid boundary
    moving special values toward the frame or opposite edge if match is found or not.

    Concepts:
    - Frame detection: Identifies bracket-like frames using grid boundaries
    - Value classification: Distinguishes between background, frame, and special values
    - Spatial transformation: move toward the frame or opposite edge if match is found or not.
    
    Transformation steps:
    1. Identify the frame value, its inner and outer background values 
    2. Find the boundary coordinates of the frame
    3. For each direction (top, bottom, left, right):
       - If a special value appears once in a row/column, move it to the frame edge
       - If multiple special values appear, move them to the grid edge
    """
    
    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()
    nrows, ncols = input_grid.shape

    # Detect background and frame values using grid boundaries
    boundaries = [input_grid[0,:], input_grid[-1,:], input_grid[:,0], input_grid[:,-1]]
    outer_background_val = None
    frame_val = None
    inner_background_val = None
    
    for b in boundaries:
        unique_vals = np.unique(b)
        if len(unique_vals) == 1:
            outer_background_val = unique_vals[0]
        if len(unique_vals) == 2:
            if b[0] == b[-1]:
                frame_val = b[0]
                inner_background_val = [v for v in unique_vals if v != frame_val][0]

    # Find frame boundaries
    frame_pos = np.argwhere(input_grid == frame_val)
    min_row, min_col = np.min(frame_pos, axis=0)  
    max_row, max_col = np.max(frame_pos, axis=0) 

    # Process bottom frame (when frame doesn't touch top)
    if min_row != 0:  # frame is touching bottom, we go column wise
        for c in range(ncols):
            col = input_grid[:, c]
            special_vals = set(col) - {inner_background_val, outer_background_val, frame_val}
            # if there is only one special value (matching case)
            if len(special_vals) == 1:
                special_val = list(special_vals)[0]  
                pos = np.where(col == special_val)[0]
                
                min_r = np.min(pos)
                # move it along the column to just outside edge of the frame
                output_grid[min_r, c] = outer_background_val
                output_grid[min_row - 1, c] = special_val
            else:  # if there are more than one special value (non matching case)
                for special_val in special_vals:
                    pos = np.where(col == special_val)[0]
                    min_r = np.min(pos)
                    if min_r < min_row:  # this value is outside the frame, move it to the top
                        output_grid[min_r, c] = outer_background_val
                        output_grid[0, c] = special_val
                        
    # Process right frame (when frame doesn't touch left)
    if min_col != 0:  # frame is touching right, we go row wise
        for r in range(nrows):
            row = input_grid[r, :]
            special_vals = set(row) - {inner_background_val, outer_background_val, frame_val}
            # if there is only one special value (matching case)
            if len(special_vals) == 1:
                special_val = list(special_vals)[0]
                pos = np.where(row == special_val)[0]
                min_c = np.min(pos)
                # move it along the row to just outside edge of the frame
                output_grid[r, min_c] = outer_background_val
                output_grid[r, min_col - 1] = special_val
            else:  # if there are more than one special value (non matching case)
                for special_val in special_vals:
                    pos = np.where(row == special_val)[0]
                    min_c = np.min(pos)
                    if min_c < min_col:  # this value is outside the frame, move it to the left
                        output_grid[r, min_c] = outer_background_val
                        output_grid[r, 0] = special_val
                        
    # Process left frame (when frame doesn't touch right)
    if max_col != ncols - 1:  # frame is touching left, we go row wise
        for r in range(nrows):
            row = input_grid[r, :]
            special_vals = set(row) - {inner_background_val, outer_background_val, frame_val}
            # if there is only one special value (matching case)
            if len(special_vals) == 1:
                special_val = list(special_vals)[0]
                pos = np.where(row == special_val)[0]
                max_c = np.max(pos)
                # move it along the row to just outside edge of the frame
                output_grid[r, max_c] = outer_background_val
                output_grid[r, max_col + 1] = special_val
            else:  # if there are more than one special value (non matching case)
                for special_val in special_vals:
                    pos = np.where(row == special_val)[0]
                    max_c = np.max(pos)
                    if max_c > max_col:  # this value is outside the frame, move it to the right
                        output_grid[r, max_c] = outer_background_val
                        output_grid[r, ncols - 1] = special_val
                        
    # Process top frame (when frame doesn't touch bottom)
    if max_row != nrows - 1:  # frame is touching top, we go column wise
        for c in range(ncols):
            col = input_grid[:, c]
            special_vals = set(col) - {inner_background_val, outer_background_val, frame_val}
            # if there is only one special value (matching case)
            if len(special_vals) == 1:
                special_val = list(special_vals)[0]
                pos = np.where(col == special_val)[0]
                max_r = np.max(pos)
                # move it along the column to just outside edge of the frame
                output_grid[max_r, c] = outer_background_val
                output_grid[max_row + 1, c] = special_val
            else:  # if there are more than one special value (non matching case)
                for special_val in special_vals:
                    pos = np.where(col == special_val)[0]
                    max_r = np.max(pos)
                    if max_r > max_row:  # this value is outside the frame, move it to the bottom
                        output_grid[max_r, c] = outer_background_val
                        output_grid[nrows - 1, c] = special_val
                        
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_7d7772cc(input_grid)
    return _result
