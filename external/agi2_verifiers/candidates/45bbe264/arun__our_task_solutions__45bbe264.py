"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 45bbe264
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__45bbe264
"""
from __future__ import annotations



import numpy as np

def solve_45bbe264(input_grid):
    """
    Concepts:
    - Expand non-zero values along their rows and columns.
    - Place value 2 at the intersections of expanded rows and columns.
 
    Steps:
    1. Find all non-zero positions.
    2. For each non-zero position, extend its value along its row and column.
    3. Place value 2 at intersections between the expanded rows and columns.
    """
 
    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()
   
    # Find positions of non-zero values
    positions_non_zero = np.argwhere(input_grid != 0)
   
    # Expand each non-zero value along its row and column
    for pos in positions_non_zero:
        r, c = tuple(pos)
        value = input_grid[r, c]
        output_grid[r, :] = value  # Fill row
        output_grid[:, c] = value  # Fill column
   
    # Place value 2 at intersections
    for i in range(len(positions_non_zero)):
        for j in range(i + 1, len(positions_non_zero)):
            r1, c1 = tuple(positions_non_zero[i])
            r2, c2 = tuple(positions_non_zero[j])
            # At the intersection points, place value 2
            output_grid[r1, c2] = 2
            output_grid[r2, c1] = 2
   
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_45bbe264(input_grid)
    return _result
