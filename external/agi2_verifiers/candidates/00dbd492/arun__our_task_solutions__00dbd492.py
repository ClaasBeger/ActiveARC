"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 00dbd492
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__00dbd492
"""
from __future__ import annotations



import numpy as np

def solve_00dbd492(input_grid):
    """
    Concepts: ring detection, interior filling

    Steps:
    1. Identify connected rings of 2s.
    2. Compute bounding box and radius of each ring.
    3. Fill the enclosed interior with a value based on radius,
       while preserving the original center cell as it carries 2.
    """
    from grid_utils import group_connected_positions

    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()

    # find all connected rings formed by 2s
    rings = group_connected_positions(np.argwhere(input_grid == 2))

    for ring in rings:
        ring = np.array(ring)
        min_row, max_row = ring[:, 0].min(), ring[:, 0].max()
        min_col, max_col = ring[:, 1].min(), ring[:, 1].max()
        center_row, center_col = (min_row + max_row) // 2, (min_col + max_col) // 2
        radius = max(max_row - center_row, max_col - center_col) - 1

        # decide fill value by radius
        fill_map = {1: 8, 2: 4, 3: 3}
        if radius in fill_map:
            output_grid[min_row+1:max_row, min_col+1:max_col] = fill_map[radius]
            # restore center cell
            output_grid[center_row, center_col] = input_grid[center_row, center_col]

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_00dbd492(input_grid)
    return _result
