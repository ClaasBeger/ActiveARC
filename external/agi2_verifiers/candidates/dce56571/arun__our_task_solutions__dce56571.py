"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: dce56571
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__dce56571
"""
from __future__ import annotations



import numpy as np

def solve_dce56571(input_grid):
    """
    Count non-background cells in the input grid and draw a centered horizontal line of that color and size in the middle row of the output grid
    initialized with the background color.
 
    Concept:
    - frequency (number of occurrences) analysis
    - count non-background cells
    - draw centered horizontal line of that color and size in middle row
 
    Transformation Steps:
        1. Identify the background color and the non-background color.
        2. Count the number of non-background colored cells.
        3. Create the output grid with the background color.
        4. Create a horizontal line of the non-background color in the middle row.
    """
 
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
 
    # Find unique colors and their counts
    unique, counts = np.unique(input_grid, return_counts=True)
    order = np.argsort(-counts)
    background = unique[order[0]]
 
    # Initialize output grid with background color
    output_grid = np.full((nrows, ncols), background)
 
    # Assuming only one non-background color (most frequent after background)
    num_non_bg = counts[order[1]]
    non_bg_val = unique[order[1]]
 
    # Calculate starting column for centering the line
    start = (ncols - num_non_bg) // 2
 
    # Place the horizontal line in the middle row
    output_grid[nrows // 2, start:start + num_non_bg] = non_bg_val
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_dce56571(input_grid)
    return _result
