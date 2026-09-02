"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 7e02026e
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__7e02026e
"""
from __future__ import annotations



import numpy as np

def solve_7e02026e(input_grid):
    """
    Find and fill '+' shaped free spaces (all 0s) with 3s
    
    Concepts:
    - Pattern detection
    - Region filling

    Transformation Steps:
    1. Scan the grid for '+' shaped regions where all five cells are free (with 0s).
       The '+' shape consists of:
       - Center: (r+1, c+1)
       - Top: (r, c+1)
       - Bottom: (r+2, c+1)
       - Left: (r+1, c)
       - Right: (r+1, c+2)
    2. For each such region, fill the entire '+' shape with 3s.
    3. Return the modified grid.
    """
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()

    # Find and fill '+' shaped free spaces (all 0s) with 3s
    for r in range(nrows - 2):
        for c in range(ncols - 2):
            if (
                input_grid[r, c+1] == 0 and
                input_grid[r+1, c] == 0 and
                input_grid[r+1, c+1] == 0 and
                input_grid[r+1, c+2] == 0 and
                input_grid[r+2, c+1] == 0
            ):
                output_grid[r, c+1] = 3
                output_grid[r+1, c] = 3
                output_grid[r+1, c+1] = 3
                output_grid[r+1, c+2] = 3
                output_grid[r+2, c+1] = 3

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_7e02026e(input_grid)
    return _result
