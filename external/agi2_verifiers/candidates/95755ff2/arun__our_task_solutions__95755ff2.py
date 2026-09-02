"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 95755ff2
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__95755ff2
"""
from __future__ import annotations



import numpy as np

def solve_95755ff2(input_grid):
    """
    Diamond-fill: take non-zero border values (except 2) and propagate them
    inward along diamond-shaped columns/rows until they hit another value
    or the diamond boundary.
    
    Concept
    - Diamond frame recognition: Detect the diamond-shaped frame of 2s in the grid. (optional)
    - Border seeding: Take border values (non-zero, not 2) from the outermost rows/columns.
    - Value propagation: Spread these border values inward along rows/columns, constrained by the diamond boundary.
    - Selective filling: Only fill empty (0) cells inside the diamond, preserving existing values (including the 2 frame).

    Transformation Steps

    1. Identify the diamond-shaped frame made of 2s. (optional)
    2. Collect non-zero, non-2 values from the grid’s top, bottom, left, and right borders.
    3. For each collected border value:
        - If from top/bottom → propagate vertically inside the diamond.
        - If from left/right → propagate horizontally inside the diamond.
    4.Stop propagation when hitting another non-zero cell or the diamond’s edge.
    5. Return the updated grid with filled values inside the diamond.
    """
    
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()

    mid_row, mid_col = nrows // 2, ncols // 2

    # Fill columns (vertical patterns from top and bottom borders)
    for c in range(1, ncols-1):
        # Process top border value
        value = input_grid[0, c]
        if value not in [0, 2]:
            if c < mid_col:  # Left side
                for r in range(mid_row - c + 1, mid_row + c):
                    if 0 <= r < nrows and output_grid[r, c] == 0:
                        output_grid[r, c] = value
                    else:
                        break
            elif c > mid_col:  # Right side
                for r in range(c - mid_col + 1, ncols - (c - mid_col + 1)):
                    if 0 <= r < nrows and output_grid[r, c] == 0:
                        output_grid[r, c] = value
                    else:
                        break
        
        # Process bottom border value
        value = input_grid[nrows-1, c]
        if value not in [0, 2]:
            if c < mid_col:  # Left side
                for r in range(mid_row + c - 1, mid_row - c, -1):
                    if 0 <= r < nrows and output_grid[r, c] == 0:
                        output_grid[r, c] = value
                    else:
                        break
            elif c > mid_col:  # Right side
                for r in range(ncols - (c - mid_col) - 2, c - mid_col - 1, -1):
                    if 0 <= r < nrows and output_grid[r, c] == 0:
                        output_grid[r, c] = value
                    else:
                        break

    # Fill rows (horizontal patterns from left and right borders)
    for r in range(1, nrows-1):
        # Process left border value
        value = input_grid[r, 0]
        if value not in [0, 2]:
            if r < mid_row:  # Top half
                for c in range(mid_col - r + 1, mid_col + r):
                    if 0 <= c < ncols and output_grid[r, c] == 0:
                        output_grid[r, c] = value
                    else:
                        break
            elif r > mid_row:  # Bottom half
                for c in range(r - mid_row + 1, ncols - (r - mid_row + 1)):
                    if 0 <= c < ncols and output_grid[r, c] == 0:
                        output_grid[r, c] = value
                    else:
                        break
        
        # Process right border value
        value = input_grid[r, ncols-1]
        if value not in [0, 2]:
            if r < mid_row:  # Top half
                for c in range(ncols - (mid_row - r) - 1, mid_col, -1):
                    if 0 <= c < ncols and output_grid[r, c] == 0:
                        output_grid[r, c] = value
                    else:
                        break
            elif r > mid_row:  # Bottom half
                for c in range(ncols - (r - mid_row) - 2, r - mid_row - 1, -1):
                    if 0 <= c < ncols and output_grid[r, c] == 0:
                        output_grid[r, c] = value
                    else:
                        break
    
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_95755ff2(input_grid)
    return _result
