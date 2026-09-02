"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 03560426
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__03560426
"""
from __future__ import annotations



import numpy as np

def solve_03560426(input_grid):
    """
    Stack colored blocks from bottom to the left edge, keeping the same order.
    
    Concepts:
    - Pattern extraction: Identifying connected regions (ractangular-blocks) of same color
    - Block arrangement: Stacking blocks with overlapping corners
    - Spatial reorganization: Placing blocks in a stair-like pattern
    
    Transformation Steps:
    1. Identify distinct colors from the bottom row of input grid
    2. For each color, extract its bounding box from the input grid
    3. Arrange these blocks starting from top-left, with each subsequent block
       overlapping at corners in a diagonal stair pattern
    """
    
    # Convert to numpy array
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = np.zeros_like(input_grid)

    # Extract unique non-zero elements from bottom row (preserve order)
    non_zero_vals = []
    for c in range(ncols):
        val = input_grid[-1, c]
        if val != 0 and val not in non_zero_vals:
            non_zero_vals.append(val)

    # Starting position for the first block
    min_r, min_c = 0, 0
    
    # Place each block in sequence with overlapping corners
    for val in non_zero_vals:
        # Find all positions with the current value
        positions = np.argwhere(input_grid == val)
        
        # Determine bounding box
        min_row, min_col = positions.min(axis=0)
        max_row, max_col = positions.max(axis=0)
        
        # Extract the block
        block = input_grid[min_row:max_row+1, min_col:max_col+1]

        # Place block at current position
        height, width = block.shape
        output_grid[min_r:min_r + height, min_c:min_c + width] = block

        # Move to next position with overlapping corners
        # (bottom-right of current block connects to top-left of next block)
        min_r += (height - 1)
        min_c += (width - 1)

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_03560426(input_grid)
    return _result
