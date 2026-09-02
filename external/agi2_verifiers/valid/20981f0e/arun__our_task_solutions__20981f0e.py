"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 20981f0e
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__20981f0e
"""
from __future__ import annotations



import numpy as np

def solve_20981f0e(input_grid):
    """
    Centers blocks of 1s within squares defined by corners marked with 2s.
    
    Concepts:
    - Grid pattern centering
    - Bounding box computation
    - Shape repositioning
    
    Transformation Steps:
    1. Identify squares defined by 2s at their corners
    2. Find a sub-block of 1s within each square
    3. Center these blocks within their respective squares
    """
    
    # Convert to numpy array
    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()
    
    # Find positions containing value 2 (corner markers)
    pos_with_2 = np.argwhere(input_grid == 2)
    rows_with_2 = np.sort(np.unique([r for r, c in pos_with_2]))
    cols_with_2 = np.sort(np.unique([c for r, c in pos_with_2]))
    size = rows_with_2[1] - rows_with_2[0] - 1 

    # Process each square defined by corner markers
    for i in range(len(rows_with_2)):
        for j in range(len(cols_with_2)):
            # Define square boundaries
            row_start = rows_with_2[i] + 1
            row_end = rows_with_2[i] + 1 + size
            col_start = cols_with_2[j] + 1
            col_end = cols_with_2[j] + 1 + size

            # Extract the block within this square
            block = input_grid[row_start:row_end, col_start:col_end]
            H, W = block.shape
            
            # Find positions of 1s within the block
            pos_with_1 = np.argwhere(block == 1)
            
            if len(pos_with_1) > 0:
                # Get bounding box of the pattern of 1s
                min_r, min_c = pos_with_1.min(axis=0) 
                max_r, max_c = pos_with_1.max(axis=0)
                
                # Extract the pattern of 1s
                sub_block = block[min_r:max_r+1, min_c:max_c+1]
                h, w = sub_block.shape
                
                # Calculate offsets for centering
                half_diff_h = (H-h) // 2
                half_diff_w = (W-w) // 2
                
                # Create new centered block
                new_block = np.zeros_like(block)
                new_block[half_diff_h:half_diff_h+h, half_diff_w:half_diff_w+w] = sub_block

                # Replace the block in the output grid with the centered block
                output_grid[row_start:row_end, col_start:col_end] = 0
                output_grid[row_start:row_end, col_start:col_end] = new_block

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_20981f0e(input_grid)
    return _result
