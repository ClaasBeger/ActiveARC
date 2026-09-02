"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e7dd8335
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__e7dd8335
"""
from __future__ import annotations



import numpy as np

def solve_e7dd8335(input_grid):
    """
    Concepts: Shape identification and color transformation for vertical mirror symmetry.

    Transformation steps:
    1. Identify all positions containing value 1 in the grid
    2. Determine the bounding box of the shape formed by these positions
    3. Calculate the vertical midpoint of the shape
    4. Replace all values below the midpoint with color 2, creating a mirror image (two-tone) effect
    """

    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()

    # Find all positions with value 1
    pos_with_1 = np.argwhere(input_grid == 1)
    
    # Skip processing if no values of 1 are found
    if len(pos_with_1) == 0:
        return output_grid
        
    # Determine bounding box of the shape
    min_row, min_col = pos_with_1.min(axis=0)
    max_row, max_col = pos_with_1.max(axis=0)
    
    # Calculate dimensions of the bounding box
    height = max_row - min_row + 1
    width = max_col - min_col + 1
    
    # Calculate the vertical midpoint
    half_height = height // 2
    midpoint_row = min_row + half_height - 1
    
    # Replace values in the lower half of the shape with 2
    # This creates a mirror image (two-tone) effect with vertical symmetry
    for p in pos_with_1:
        r, c = p
        if r > midpoint_row:
            output_grid[r, c] = 2
            
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_e7dd8335(input_grid)
    return _result
