"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 5ffb2104
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__5ffb2104
"""
from __future__ import annotations



import numpy as np

def solve_5ffb2104(input_grid):
    """
    Concepts: horizontally shift connected non-zero blocks (connectivity=4)
              to the right until they hit either the grid boundary
              or another non-zero block.

    Transformation steps:
    1. Identify connected non-zero blocks for each unique value.
    2. Process blocks in order of their rightmost column (rightmost first).
    3. For each block, compute the maximum feasible right shift.
    4. Clear original positions and place the block at its shifted location.
    """
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()

    from grid_utils import group_connected_positions

    # Step 1: Identify connected non-zero blocks
    non_zero_vals = np.unique(input_grid[input_grid != 0])
    all_parts = []
    max_cols = []
    for val in non_zero_vals:
        position = np.argwhere(input_grid == val)
        parts = group_connected_positions(position, connectivity=4)
        for part in parts:
            part = np.array(part)
            max_col = part[:, 1].max()  # Get the maximum column index of the part
            all_parts.append(part)
            max_cols.append(max_col)

    # Step 2: Process each block in the order: from rightmost to leftmost
    order = np.argsort(max_cols)[::-1]
    for i in order:
        part = all_parts[i]
        min_row, max_row = min(part[:, 0]), max(part[:, 0])
        max_col = max_cols[i]
        # If the block is already at the rightmost position, skip it
        if max_col == ncols - 1:
            continue
        else: # Step 3: Compute maximum feasible right shift
            final_shift = 0
            for shift in range(1, ncols):
                if max_col + shift >= ncols:
                    break
                else:
                    if output_grid[min_row:max_row + 1, max_col + shift].any()!=0: # Check for collisions
                        break
                    else:
                        final_shift += 1
            # Step 4: Apply shift
            for r, c in part:
                output_grid[r, c] = 0
                output_grid[r, c+final_shift] = input_grid[r, c]

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_5ffb2104(input_grid)
    return _result
