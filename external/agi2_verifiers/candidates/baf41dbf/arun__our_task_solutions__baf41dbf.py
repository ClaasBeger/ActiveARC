"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: baf41dbf
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__baf41dbf
"""
from __future__ import annotations



import numpy as np

def solve_baf41dbf(input_grid):
    """
    Concepts: Region growth, without changing topology, the direction of marks until they are hit.

    Transformation steps:
    1. Identify connected components of 3s.
    2. Extend the grid of 3s outward in the direction of every mark 6 until it is hit.
    3. Ensure all interior rows and columns containing 3s are fully expanded.
    """
    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()

    # Step 1: Identify rows and columns containing 6
    rows_with_6, cols_with_6 = np.where(input_grid == 6)

    def expand(grid, r, c):
        """
        Expands the region of 3s outward from the given row and column (r, c) of a mark 6.
        """
        rows_with_3, cols_with_3 = np.where(grid == 3)
        if len(rows_with_3) == 0 or len(cols_with_3) == 0:
            return grid  # No 3s to expand

        row_min_3, row_max_3 = rows_with_3.min(), rows_with_3.max()
        col_min_3, col_max_3 = cols_with_3.min(), cols_with_3.max()

        # Expand upwards
        if r < row_min_3:
            c_positions = np.where(grid[row_min_3 + 1] == 3)[0]
            cmin, cmax = c_positions.min(), c_positions.max()
            grid[row_min_3, cmin:cmax + 1] = 0  # Clear the original row
            grid[r + 1, cmin:cmax + 1] = 3  # Fill the row adjacent to the mark 6
            for cc in c_positions:
                grid[r + 1:row_min_3 + 1, cc] = 3  # Fill the column-parts

        # Expand downwards
        if r > row_max_3:
            c_positions = np.where(grid[row_max_3 - 1] == 3)[0]
            cmin, cmax = c_positions.min(), c_positions.max()
            grid[row_max_3, cmin:cmax + 1] = 0  # Clear the original row
            grid[r - 1, cmin:cmax + 1] = 3  # Fill the row adjacent to the mark 6
            for cc in c_positions:
                grid[row_max_3:r, cc] = 3  # Fill the column-parts

        # Expand leftwards
        if c < col_min_3:
            r_positions = np.where(grid[:, col_min_3 + 1] == 3)[0]
            rmin, rmax = r_positions.min(), r_positions.max()
            grid[rmin:rmax + 1, col_min_3] = 0  # Clear the original column
            grid[rmin:rmax + 1, c + 1] = 3  # Fill the column adjacent to the mark 6
            for rr in r_positions:
                grid[rr, c + 1:col_min_3 + 1] = 3  # Fill the row-parts

        # Expand rightwards
        if c > col_max_3:
            r_positions = np.where(grid[:, col_max_3 - 1] == 3)[0]
            rmin, rmax = r_positions.min(), r_positions.max()
            grid[rmin:rmax + 1, col_max_3] = 0  # Clear the original column
            grid[rmin:rmax + 1, c - 1] = 3  # Fill the column adjacent to the mark 6
            for rr in r_positions:
                grid[rr, col_max_3:c] = 3  # Fill the row-parts

        return grid

    # Step 2: Extend the grid of 3s outward in the direction of every mark 6 until it is hit
    for r, c in zip(rows_with_6, cols_with_6):
        output_grid = expand(output_grid, r, c)

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_baf41dbf(input_grid)
    return _result
