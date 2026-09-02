"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ce039d91
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__ce039d91
"""
from __future__ import annotations



import numpy as np

def solve_ce039d91(input_grid):
    """
    Paint the left-right symmetric non-background part in color 1.
 
    Concept:
        - Identify the background color (most frequent).
        - For each non-background cell, if its horizontal mirror is also non-background, paint both positions with color 1.
 
    Steps:
        1. Find the background and non-background colors.
        2. For each non-background cell, check its horizontal symmetric cell.
        3. If both are non-background, set both to color 1.
    """
    import numpy as np
 
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = np.copy(input_grid)
 
    # Identify background color (most frequent)
    unique_colors, counts = np.unique(input_grid, return_counts=True)
    order = np.argsort(-counts)  # descending order
    background_color = unique_colors[order[0]]
    non_bg_color = unique_colors[order[1]]
 
    # Paint symmetric non-background pairs in color 1
    non_bg_pos = np.argwhere(input_grid != background_color)
    for r, c in non_bg_pos:
        sym_c = ncols - 1 - c
        if input_grid[r, sym_c] == non_bg_color:
            output_grid[r, c] = 1
            output_grid[r, sym_c] = 1
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_ce039d91(input_grid)
    return _result
