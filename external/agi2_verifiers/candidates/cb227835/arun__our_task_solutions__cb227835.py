"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: cb227835
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__cb227835
"""
from __future__ import annotations



import numpy as np

def solve_cb227835(input_grid):
    """
    Identifies two 8s in the input grid that are closest to opposite corners,
    then connects them with lines of 3s to form a boundary structure.
    
    Concepts:
    - Pattern recognition: Identifying 8s positioned near opposite corners
    - Boundary creation: Connecting corner elements with straight lines to form a boundary structure.
    - Grid transformation: Converting elements along line to value (color) 3
    
    Transformation Steps:
    1. Find all positions containing value 8 in the input grid
    2. Identify if 8s are positioned along main diagonal (top-left to bottom-right)
       or anti-diagonal (top-right to bottom-left)
    3. Draw lines of 3s connecting the 8s:
       a. Along diagonal paths between the 8s
       b. Vertically/ horizontally from 8s to form a boundary structure.
    """
    
    # Convert input to numpy array
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()
    
    # Find all positions containing the value 8
    pos_with_8 = np.argwhere(input_grid == 8)
    
    # Get minimum and maximum row and column coordinates of 8s
    min_row, min_col = np.min(pos_with_8, axis=0)
    max_row, max_col = np.max(pos_with_8, axis=0)
    pos_with_8 = set(map(tuple, pos_with_8))
  
    if (min_row, min_col) in pos_with_8 and (max_row, max_col) in pos_with_8:
        # Case 1: 8s are positioned along main diagonal (top-left to bottom-right)
        
        # Draw diagonal line from top-left 8 downward and rightward
        for i in range(1, max(nrows, ncols)):
            r, c = min_row + i, min_col + i
            if 0 <= r < nrows and 0 <= c <= max_col:
                output_grid[r, c] = 3
            else:
                break
        
        # Draw diagonal line from bottom-right 8 upward and leftward
        for i in range(1, max(nrows, ncols)):
            r, c = max_row - i, max_col - i
            if 0 <= r < nrows and min_col <= c < ncols:
                output_grid[r, c] = 3
            else:
                break
                
        # Draw vertical line down from top-left 8
        for i in range(min_row+1, nrows):
            if output_grid[i, min_col] == 0:
                output_grid[i, min_col] = 3
            else:
                break
                
        # Draw vertical line up from bottom-right 8
        for i in range(max_row-1, -1, -1):
            if output_grid[i, max_col] == 0:
                output_grid[i, max_col] = 3
            else:
                break
                
    elif (min_row, max_col) in pos_with_8 and (max_row, min_col) in pos_with_8:
        # Case 2: 8s are positioned along anti-diagonal (top-right to bottom-left)
        
        # Draw diagonal line from top-right 8 downward and leftward
        for i in range(1, max(nrows, ncols)):
            r, c = min_row + i, max_col - i
            if 0 <= r <= max_row and 0 <= c < ncols:
                output_grid[r, c] = 3
            else:
                break
        
        # Draw diagonal line from bottom-left 8 upward and rightward
        for i in range(1, max(nrows, ncols)):
            r, c = max_row - i, min_col + i
            if min_row <= r < nrows and 0 <= c < ncols:
                output_grid[r, c] = 3
            else:
                break
                
        # Draw horizontal line right from bottom-left 8
        for i in range(min_col+1, ncols):
            if output_grid[max_row, i] == 0:
                output_grid[max_row, i] = 3
            else:
                break
                
        # Draw horizontal line left from top-right 8
        for i in range(max_col-1, -1, -1):
            if output_grid[min_row, i] == 0:
                output_grid[min_row, i] = 3
            else:
                break
        
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_cb227835(input_grid)
    return _result
