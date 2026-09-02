"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 60a26a3e
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__60a26a3e
"""
from __future__ import annotations



import numpy as np

def solve_60a26a3e(input_grid):
    """
    Concepts: object of certain shape and it center detection, line filling, connecte component.

    Transformation steps:
    1. Find all positions with value 2 and group them into connected components (8-connectivity).
    2. For each component, compute its center.
    3. For all centers sharing the same row, fill horizontal lines between them with value 1 (excluding endpoints).
    4. For all centers sharing the same column, fill vertical lines between them with value 1 (excluding endpoints).
    """
    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()

    positions = np.argwhere(input_grid == 2)
    from grid_utils import group_connected_positions

    # Step 1: Group positions into connected components (they will be of same shape like +)
    parts = group_connected_positions(positions, connectivity=8)

    # Step 2: Compute centers of each component
    centers = []
    for part in parts:
        part = np.array(part)
        min_row, min_col = part.min(axis=0)
        max_row, max_col = part.max(axis=0)
        center_row = (min_row + max_row) // 2
        center_col = (min_col + max_col) // 2
        centers.append([center_row, center_col])

    centers = np.array(centers)
    cen_rows = np.unique(centers[:, 0])
    cen_cols = np.unique(centers[:, 1])

    # Step 3: Fill horizontal lines between centers in the same row
    for r in cen_rows:
        r_pos = np.where(centers[:, 0] == r)[0]
        if r_pos.size > 1:
            r_cen = centers[r_pos]
            sorted_idx = np.lexsort((r_cen[:, 1], r_cen[:, 0]))
            r_cen = r_cen[sorted_idx]
            for i in range(len(r_cen) - 1):
                cen1, cen2 = r_cen[i], r_cen[i + 1]
                min_c, max_c = min(cen1[1], cen2[1]), max(cen1[1], cen2[1])
                output_grid[r, min_c + 2:max_c - 1] = 1

    # Step 4: Fill vertical lines between centers in the same column
    for c in cen_cols:
        c_pos = np.where(centers[:, 1] == c)[0]
        if c_pos.size > 1:
            c_cen = centers[c_pos]
            sorted_idx = np.lexsort((c_cen[:, 1], c_cen[:, 0]))
            c_cen = c_cen[sorted_idx]
            for i in range(len(c_cen) - 1):
                cen1, cen2 = c_cen[i], c_cen[i + 1]
                min_r, max_r = min(cen1[0], cen2[0]), max(cen1[0], cen2[0])
                output_grid[min_r + 2:max_r - 1, c] = 1

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_60a26a3e(input_grid)
    return _result
