"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: f0afb749
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__f0afb749
"""
from __future__ import annotations



import numpy as np

def solve_f0afb749(input_grid):
    """
    Concepts: value expansion, diagonal patterning

    Transformation: Expand each non-zero cell to a 2×2 block, then extend diagonally with 2×2 [[1,0], [0,1]] patterns.

    Transformation steps:
    1. Identify all non-background (non-zero) values and their positions (r, c) in the input grid.
    2. Create an output grid of size (2*nrows, 2*ncols) filled with zeros.
    3. For each non-background value v:
       a. Place a 2×2 block filled with v at position (2*r, 2*c).
       b. From the center of that block, move along both diagonal directions:
          - (-1, -1), (-2, -2), ... upward-left
          - (+1, +1), (+2, +2), ... downward-right
         At each such position, place the fixed pattern [[1, 0], [0, 1]] (without overwriting existing non-zero values).
    """
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape

    # Initialize output grid with double the size of input grid to the background value (0)
    output_grid = np.zeros((nrows * 2, ncols * 2), dtype=int)

    # Step 1: find all non-zero (non-background) positions
    nonzero_positions = np.argwhere(input_grid != 0)

    for r, c in nonzero_positions:
        v = input_grid[r, c]
        # Step 3a: expand original cell to 2×2 block with value v
        output_grid[2*r:2*r+2, 2*c:2*c+2] = v

        # Step 3b: place diagonal [[1,0],[0,1]] patterns
        for dr, dc in [(-1, -1), (1, 1)]:
            rr, cc = r + dr, c + dc
            while 0 <= rr < nrows and 0 <= cc < ncols:
                R, C = 2*rr, 2*cc
                pattern = np.array([[1, 0], [0, 1]])
                mask = (output_grid[R:R+2, C:C+2] == 0)
                output_grid[R:R+2, C:C+2] = np.where(mask, pattern, output_grid[R:R+2, C:C+2])
                rr += dr
                cc += dc

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_f0afb749(input_grid)
    return _result
