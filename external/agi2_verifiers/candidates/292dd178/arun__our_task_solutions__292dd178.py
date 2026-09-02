"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 292dd178
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__292dd178
"""
from __future__ import annotations



import numpy as np

def solve_292dd178(input_grid):
    """
    Concepts: Source is emitting substance (2)

    Transformation steps:
    1. Find connected blocks of 1s that form sources
    2. Fill their interior with 2s (substance)
    3. Detect the opening (cell with most frequent background value).
    4. Extend 2s as a stream of substance from the opening outward till the grid boundary is reached.
    """
    from grid_utils import group_connected_positions

    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()

    values, counts = np.unique(input_grid, return_counts=True)
    background = values[np.argmax(counts)]  # most frequent value
    
    positions = np.argwhere(input_grid == 1)
    parts = group_connected_positions(positions)

    for part in parts:
        part = np.array(part)
        min_row, min_col = part.min(axis=0)
        max_row, max_col = part.max(axis=0)

        # fill interior
        output_grid[min_row+1:max_row, min_col+1:max_col] = 2

        block = output_grid[min_row:max_row+1, min_col:max_col+1]
        r, c = np.argwhere(block == background)[0]  # opening position

        if r == 0:
            output_grid[:min_row+1, min_col+c] = 2 # stream of 2s from the opening to the top
        elif c == 0:
            output_grid[min_row+r, :min_col+1] = 2 # stream of 2s from the opening to the left
        elif r == block.shape[0]-1:
            output_grid[min_row+r:, min_col+c] = 2 # stream of 2s from the opening to the bottom    
        elif c == block.shape[1]-1:
            output_grid[min_row+r, min_col+c:] = 2 # stream of 2s from the opening to the right

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_292dd178(input_grid)
    return _result
