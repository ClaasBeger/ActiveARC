"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 17b80ad2
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__17b80ad2
"""
from __future__ import annotations



import numpy as np

def solve_17b80ad2(input_grid):
    """
    Fills columns upward from bottom markers (color 5), changing color when a non-zero cell is encountered.
 
    Concept:
        - Markers are given in the bottom row with color 5.
        - For each marker column, fill upwards with the current color.
        - When a non-zero color is encountered, update the fill color to that value.
 
    Transformation Steps:
        1. For each column, if the bottom cell is a marker (5), fill upwards.
        2. At each step, if the input cell is zero, fill with the current color.
        3. If a non-zero cell is encountered, update the current color to that value and continue.
    """
    import numpy as np
 
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()
   
    # Set the marker color 5
    marker_color = 5
 
    for c in range(ncols):
        if output_grid[nrows - 1, c] == marker_color:
            # initialize color to marker color
            color = marker_color
            for r in range(nrows - 1, -1, -1):
                if input_grid[r, c] == 0: # if cell is empty (with background color 0), fill with current color
                    output_grid[r, c] = color
                else: # update color to the encountered non-zero color
                    color = input_grid[r, c]
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_17b80ad2(input_grid)
    return _result
