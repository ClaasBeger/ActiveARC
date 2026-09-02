"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 13f06aa5
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__13f06aa5
"""
from __future__ import annotations



import numpy as np

def solve_13f06aa5(input_grid):
    """
    Concepts: Source firing objects to the grid wall, Directional propagation, unique value extension,

    Transformation steps:
    1. Identify unique values (appearing once) in the grid.
    2. For each, extend its value in the direction of adjacent background cells (up, down, left, right).
    3. Fill edge and corner cells according to overlap rules.
    """

    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()

    unique, counts = np.unique(input_grid, return_counts=True)
    background = unique[np.argmax(counts)]
    selected_vals = unique[counts == 1] # objects

    for val in selected_vals:
        pos = np.argwhere(input_grid == val)[0]
        r, c = pos

        # Shoot up
        if r > 0 and input_grid[r - 1, c] == background:
            for rr in range(r - 2, -1, -2):
                output_grid[rr, c] = val
            output_grid[0, 1:-1] = val
            for r_, c_ in [(0, 0), (0, ncols - 1)]: # filling the corners
                output_grid[r_, c_] = val if output_grid[r_, c_] == background else 0

        # Shoot down
        elif r < nrows - 1 and input_grid[r + 1, c] == background:
            for rr in range(r + 2, nrows, 2):
                output_grid[rr, c] = val
            output_grid[-1, 1:-1] = val
            for r_, c_ in [(nrows - 1, 0), (nrows - 1, ncols - 1)]:
                output_grid[r_, c_] = val if output_grid[r_, c_] == background else 0

        # Shoot left
        elif c > 0 and input_grid[r, c - 1] == background:
            for cc in range(c - 2, -1, -2):
                output_grid[r, cc] = val
            output_grid[1:-1, 0] = val
            for r_, c_ in [(0, 0), (nrows - 1, 0)]:
                output_grid[r_, c_] = val if output_grid[r_, c_] == background else 0

        # Shoot right
        elif c < ncols - 1 and input_grid[r, c + 1] == background:
            for cc in range(c + 2, ncols, 2):
                output_grid[r, cc] = val
            output_grid[1:-1, -1] = val
            for r_, c_ in [(0, ncols - 1), (nrows - 1, ncols - 1)]:
                output_grid[r_, c_] = val if output_grid[r_, c_] == background else 0

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_13f06aa5(input_grid)
    return _result
