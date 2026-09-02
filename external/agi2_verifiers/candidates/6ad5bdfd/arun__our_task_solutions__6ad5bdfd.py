"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 6ad5bdfd
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__6ad5bdfd
"""
from __future__ import annotations



import numpy as np

def solve_6ad5bdfd(input_grid):
    """
    Concepts: Shift connected non-zero blocks (connectivity=4) horizontally or vertically
    until they hit the grid boundary or another non-zero block.

    Transformation steps:
    1. Identify the direction to move (based on a row or column of 2s at the grid edge).
    2. Find all connected non-zero blocks for each unique value.
    3. Process blocks in the correct order for the direction.
    4. For each block, compute the maximum feasible shift.
    5. Clear original positions and place the block at its shifted location.
    """
    from grid_utils import group_connected_positions, move_parts

    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()

    # Determine movement direction from edge 2s
    pos_with_2 = np.argwhere(input_grid == 2)
    uniq_rows = np.unique(pos_with_2[:, 0])
    uniq_cols = np.unique(pos_with_2[:, 1])
    direction = None
    if uniq_cols.size == 1:
        if uniq_cols[0] == ncols - 1:
            direction = "left to right"
        elif uniq_cols[0] == 0:
            direction = "right to left"
    elif uniq_rows.size == 1:
        if uniq_rows[0] == nrows - 1:
            direction = "top to bottom"
        elif uniq_rows[0] == 0:
            direction = "bottom to top"

    # Find all connected non-zero blocks
    non_zero_vals = np.unique(input_grid[input_grid != 0])
    all_parts = []
    for val in non_zero_vals:
        positions = np.argwhere(input_grid == val)
        parts = group_connected_positions(positions, connectivity=4)
        for part in parts:
            all_parts.append(np.array(part))

    output_grid = move_parts(all_parts, direction, output_grid, input_grid)
    
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_6ad5bdfd(input_grid)
    return _result
