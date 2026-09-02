"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 94414823
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__94414823
"""
from __future__ import annotations



import numpy as np

def solve_94414823(input_grid):
    """
    Concepts: 
        - Frame detection
        - Diagonal 2×2 block placement
    
    Transformation: Replace the two corner-adjacent numbers outside a 5-frame with 2×2 blocks of the same values placed in the frame’s diagonally.

    Transformation steps:
    1. Identify the outer frame of '5's in the grid.
    2. Detect the nonzero values just outside each corner of the frame.
    3. Place 2×2 squares of these values inside the frame along the diagonal that passes through the corner where the value was detected.
    """
    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()

    # Step 1: Find frame bounds (assuming perfect rectangle of 5s)
    rows, cols = np.where(input_grid == 5)
    rmin, rmax = rows.min(), rows.max()
    cmin, cmax = cols.min(), cols.max()

    # Step 2: Detect nonzero values just outside frame corners
    vals = {}
    if rmin-1 >= 0 and cmin-1 >= 0 and input_grid[rmin-1, cmin-1] != 0:
        vals['top_left'] = input_grid[rmin-1, cmin-1]
    if rmin-1 >= 0 and cmax+1 < input_grid.shape[1] and input_grid[rmin-1, cmax+1] != 0:
        vals['top_right'] = input_grid[rmin-1, cmax+1]
    if rmax+1 < input_grid.shape[0] and cmin-1 >= 0 and input_grid[rmax+1, cmin-1] != 0:
        vals['bottom_left'] = input_grid[rmax+1, cmin-1]
    if rmax+1 < input_grid.shape[0] and cmax+1 < input_grid.shape[1] and input_grid[rmax+1, cmax+1] != 0:
        vals['bottom_right'] = input_grid[rmax+1, cmax+1]

    # Place 2×2 squares of these values inside the frame along the diagonal that passes through the corner where the value was detected.
    if 'top_left' in vals:
        output_grid[rmin+1:rmin+3, cmin+1:cmin+3] = vals['top_left']
        output_grid[rmin+3:rmin+5, cmin+3:cmin+5] = vals['top_left']
    if 'bottom_right' in vals:
        output_grid[rmin+1:rmin+3, cmin+1:cmin+3] = vals['bottom_right']
        output_grid[rmin+3:rmin+5, cmin+3:cmin+5] = vals['bottom_right']
    if 'top_right' in vals:
        output_grid[rmin+1:rmin+3, cmax-2:cmax] = vals['top_right']
        output_grid[rmin+3:rmin+5, cmin+1:cmin+3] = vals['top_right']
    if 'bottom_left' in vals:
        output_grid[rmin+1:rmin+3, cmax-2:cmax] = vals['bottom_left']
        output_grid[rmin+3:rmin+5, cmin+1:cmin+3] = vals['bottom_left']

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_94414823(input_grid)
    return _result
