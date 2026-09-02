"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ac605cbb
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__ac605cbb
"""
from __future__ import annotations



import numpy as np

def solve_ac605cbb(input_grid):
    """
    Concept:
    - color (value) based grid transformation (drawing lines)
    - analysing intersections of newly drawn lines and drawing diagonals from there
 
    Transformation Steps:
        1. Identify non-background colors (assuming background is 0).
        2. For each non-background color, locate its position and draw line patterns with color 5 according to the color value.
        3. If the two 5 line intesect, means: For each cell with color 5 that has non-zero neighbors in all four directions (up, down, left, right),
        then draw a diagonal line of color 4 extending to the grid edge.
    """
 
 
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()
 
    # Find non-background colors (assuming background is 0)
    non_zero_vals = np.unique(input_grid[input_grid != 0])
 
    # For each non-background value, draw lines in specific directions using color 5
    for val in non_zero_vals:
        r, c = tuple(np.argwhere(input_grid == val)[0])  # Expectation: only one occurrence
        if val == 1:
            output_grid[r, c+1:c+3] = 5
            output_grid[r-1, c+2] = val
        elif val == 2:
            output_grid[r, c-3:c] = 5
            output_grid[r, c-4] = val
        elif val == 3:
            output_grid[r+1:r+3, c] = 5
            output_grid[r+3, c] = val
        elif val == 6:
            output_grid[r-5:r, c] = 5
            output_grid[r-6, c] = val
 
    # Find positions with color 5 to deal with the case of intersections
    pos_with_5 = np.argwhere(output_grid == 5)
    for p in pos_with_5:
        r, c = tuple(p)
        # If the two newly drawn 5 line intersect, means: If 5 surrounded by non-zero values in all four directions, draw diagonal line of color 4
        if (output_grid[r, c-1] != 0 and output_grid[r, c+1] != 0 and
            output_grid[r-1, c] != 0 and output_grid[r+1, c] != 0):
            for s in range(max(nrows, ncols)):
                rr, cc = r + s, c - s
                if 0 <= rr < nrows and 0 <= cc < ncols:
                    output_grid[rr, cc] = 4
                else:
                    break
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_ac605cbb(input_grid)
    return _result
