"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 7c8af763
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__7c8af763
"""
from __future__ import annotations



import numpy as np

def solve_7c8af763(input_grid):
    """
    Concepts: leakage from the neighboring values (colors) into the empty compartments
    - Find connected components of zeros in the grid, these are empty compartments.
    - For each component, examine neighboring values.
    - Fill the zero regions with the most common neighboring value out of 1 and 2.
 
    Steps:
    1. Find all positions containing zero.
    2. Group connected zero positions.
    3. For each group:
        - Determine the boundary of the zero region.
        - Collect all neighboring values around the boundary.
        - Count occurrences of values 1 and 2 among neighbors.
        - Fill the zero region with the more frequent value out of 1 and 2.
    """
    from grid_utils import group_connected_positions
 
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()
 
    # Find and group connected zeros
    zero_positions = np.argwhere(input_grid == 0)
    connected_zero_groups = group_connected_positions(zero_positions)
 
    # Process each connected zero component (empty compartment)
    for group in connected_zero_groups:
        group = np.array(group)
        min_row, min_col = group.min(axis=0)
        max_row, max_col = group.max(axis=0)
       
        # Collect all neighboring values around the boundary
        neighbors = []
       
        # Top neighbors
        if min_row > 0:
            for c in range(max(0, min_col-1), min(ncols, max_col+2)):
                neighbors.append(input_grid[min_row-1, c])
               
        # Bottom neighbors
        if max_row < nrows-1:
            for c in range(max(0, min_col-1), min(ncols, max_col+2)):
                neighbors.append(input_grid[max_row+1, c])
               
        # Left neighbors
        if min_col > 0:
            for r in range(max(0, min_row-1), min(nrows, max_row+2)):
                neighbors.append(input_grid[r, min_col-1])
               
        # Right neighbors
        if max_col < ncols-1:
            for r in range(max(0, min_row-1), min(nrows, max_row+2)):
                neighbors.append(input_grid[r, max_col+1])
       
        # Count occurrences of values 1 and 2
        neighbors = np.array(neighbors)
        count_1s = np.sum(neighbors == 1)
        count_2s = np.sum(neighbors == 2)
 
        # Fill with the more frequent value out of 1 and 2 in the empty compartment
        if count_1s > count_2s:
            output_grid[min_row:max_row+1, min_col:max_col+1] = 1
        elif count_2s > count_1s:
            output_grid[min_row:max_row+1, min_col:max_col+1] = 2
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_7c8af763(input_grid)
    return _result
