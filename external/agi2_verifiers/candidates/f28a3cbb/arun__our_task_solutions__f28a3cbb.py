"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: f28a3cbb
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__f28a3cbb
"""
from __future__ import annotations



import numpy as np

def solve_f28a3cbb(input_grid):
    """
    Gather identical values (color) to the top-left and bottom-right corners from adjacent quadrants.

    Concepts:
    - Grid partitioning
    - value gathering

    Transformation Steps:
    1. Identify the unique non-background value in the top-left and bottom-right 3x3 blocks.
    2. For the top-left 3x3 block:
       - Move any matching value from the adjacent top-right, bottom-left, and bottom-right quadrants to the border of the top-left block, 
       replacing its original position with the background color.
    3. For the bottom-right 3x3 block:
       - Move any matching value from the adjacent top-right, bottom-left, and top-left quadrants to the border of the bottom-right block, 
       replacing its original position with the background color.
    4. Return the transformed grid.
    """

    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()

    unique, counts = np.unique(input_grid, return_counts=True)
    background_color = unique[np.argmax(counts)]

    # ====== process the top-left 3x3 block ======
    top_left_block = input_grid[:3, :3]
    val = np.unique(top_left_block)[0]  # expecting only one non-background value

    # find and move the value from its top-right adjacent quadrant to the border of the top-left block
    its_top_right_block = input_grid[:3, 3:]
    pos = np.argwhere(its_top_right_block == val)
    for p in pos:
        r, c = tuple(p)
        c += 3
        output_grid[r, c] = background_color
        output_grid[r, 3] = val
    # find and move the value from its bottom-left adjacent quadrant to the border of the top-left block
    its_bottom_left_block = input_grid[3:, :3]
    pos = np.argwhere(its_bottom_left_block == val)
    for p in pos:
        r, c = tuple(p)
        r += 3
        output_grid[r, c] = background_color
        output_grid[3, c] = val
    # find and move the value from its bottom-right adjacent quadrant to the border of the top-left block
    its_bottom_right_block = input_grid[3:, 3:]
    pos = np.argwhere(its_bottom_right_block == val)
    for p in pos:
        r, c = tuple(p)
        r += 3
        c += 3
        output_grid[r, c] = background_color
        output_grid[2, 3] = val

    # ======= process the bottom-right 3x3 block ======
    bottom_right_block = input_grid[-3:, -3:]
    val = np.unique(bottom_right_block)[0]  # expecting only one non-background value
    
    # find and move the value from its top-right adjacent quadrant to the border of the bottom-right block
    its_top_right_block = input_grid[:-3, -3:]
    pos = np.argwhere(its_top_right_block == val)
    for p in pos:
        r, c = tuple(p)
        c += ncols - 3
        output_grid[r, c] = background_color
        output_grid[-4, c] = val
    # find and move the value from its bottom-left adjacent quadrant to the border of the bottom-right block
    its_bottom_left_block = input_grid[-3:, :-3]
    pos = np.argwhere(its_bottom_left_block == val)
    for p in pos:
        r, c = tuple(p)
        r += nrows - 3
        output_grid[r, c] = background_color
        output_grid[r, -4] = val
    # find and move the value from its top-left adjacent quadrant to the border of the bottom-right block
    its_top_left_block = input_grid[:-3, :-3]
    pos = np.argwhere(its_top_left_block == val)
    for p in pos:
        r, c = tuple(p)
        output_grid[r, c] = background_color
        output_grid[-3, -4] = val

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_f28a3cbb(input_grid)
    return _result
