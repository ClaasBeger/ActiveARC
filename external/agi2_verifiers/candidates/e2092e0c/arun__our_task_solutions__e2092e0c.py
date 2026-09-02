"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e2092e0c
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__e2092e0c
"""
from __future__ import annotations



import numpy as np

def solve_e2092e0c(input_grid):
    """
    Finds pattern bounded by frame of 5s and/or grid boundaries 
    draws a border of 5s around each matching pattern.

    Concepts:
    - Pattern detection: pattern bounded by frame of 5s and/or grid boundaries
    - Pattern matching: Finding occurrences of patterns within a grid
    - Border creation: Drawing borders around identified patterns
    
    Transformation Steps:
    1. Finds pattern bounded by frame of 5s and/or grid boundaries 
        - Find all positions containing 5s
        - Group connected 5s together
        - Identify the largest group of connected 5s as the frame
        - Identify the pattern within this frame
    2. Search for all occurrences of this pattern in the grid
    3. Draw a border of 5s around each pattern occurrence
    """
    from grid_utils import group_connected_positions
    
    # Convert to numpy array
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()

    # Find all positions with value 5
    pos_with_5 = np.argwhere(input_grid == 5)
    
    # Group connected positions with value 5
    groups = group_connected_positions(pos_with_5)
    
    # Find the largest connected group
    biggest_group = max(groups, key=len) if groups else []
    
    # Get the bounding box of the pattern
    min_row, max_row = min(p[0] for p in biggest_group), max(p[0] for p in biggest_group)
    min_col, max_col = min(p[1] for p in biggest_group), max(p[1] for p in biggest_group)
    
    # Extract the pattern
    pattern = input_grid[min_row:max_row, min_col:max_col]
    
    # Find all matching patterns in the grid
    height, width = pattern.shape
    for r in range(nrows - height + 1):
        for c in range(ncols - width + 1):
            subgrid = input_grid[r:r+height, c:c+width]
            
            # If pattern matches, draw a border of 5s around it
            if np.array_equal(subgrid, pattern):
                # Left and right borders
                output_grid[r-1:r + height + 1, c-1] = 5
                output_grid[r-1:r + height + 1, c + width] = 5

                # Top and bottom borders
                output_grid[r-1, c-1:c + width + 1] = 5
                output_grid[r + height, c-1:c + width + 1] = 5

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_e2092e0c(input_grid)
    return _result
