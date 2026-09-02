"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: f8be4b64
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__f8be4b64
"""
from __future__ import annotations



import numpy as np

def solve_f8be4b64(input_grid):
    """
    Concepts: Gift wrapping with ribbons — coloring rows and columns like tying ribbons on gift boxes.

    Transformation steps:
    1. Identify connected regions of value 3 (ribbon flowers).
    2. For each region, compute its center point (flower middle).
    3. From each center, extend its value horizontally, then vertically.
    4. Stop extension when another flower (3) is encountered or at grid boundary.
    """
    from grid_utils import group_connected_positions

    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()

    # Find all positions with value 3 (that make ribbon flowers)
    pos_with_3 = np.argwhere(input_grid == 3)

    # Group positions into connected components (ribbon flowers)
    parts_with_3 = group_connected_positions(pos_with_3)

    # Find middle points for each connected component
    middle_rows = []
    middle_cols = []
    middle_vals = []
    
    for part in parts_with_3:
        part = np.array(part)
        min_row, max_row = part[:, 0].min(), part[:, 0].max()
        min_col, max_col = part[:, 1].min(), part[:, 1].max()

        # Calculate center coordinates (flower middle color)
        middle_row = (min_row + max_row) // 2
        middle_col = (min_col + max_col) // 2

        middle_rows.append(middle_row)
        middle_cols.append(middle_col)
        
        # Get value at center position
        middle_val = input_grid[middle_row, middle_col]
        middle_vals.append(middle_val)

    # Process components by row order
    order = np.argsort(middle_rows)
    for i in order:
        middle_row = middle_rows[i]
        middle_col = middle_cols[i]
        middle_val = middle_vals[i]
        
        # Extend horizontally left until encountering another ribbon flower or grid boundary
        for c in range(middle_col-2, -1, -1):
            if output_grid[middle_row, c] != 3:
                output_grid[middle_row, c] = middle_val
            else:
                break

        # Extend horizontally right until encountering another ribbon flower or grid boundary
        for c in range(middle_col+2, ncols):
            if output_grid[middle_row, c] != 3:
                output_grid[middle_row, c] = middle_val
            else:
                break
    
    # Then Process components by column order
    order = np.argsort(middle_cols)
    for i in order:
        middle_row = middle_rows[i]
        middle_col = middle_cols[i]
        middle_val = middle_vals[i]

        # Extend vertically up until encountering another ribbon flower or grid boundary
        for r in range(middle_row-2, -1, -1):
            if output_grid[r, middle_col] != 3:
                output_grid[r, middle_col] = middle_val
            else:
                break

        # Extend vertically down until encountering another ribbon flower or grid boundary
        for r in range(middle_row+2, nrows):
            if output_grid[r, middle_col] != 3:
                output_grid[r, middle_col] = middle_val
            else:
                break

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_f8be4b64(input_grid)
    return _result
