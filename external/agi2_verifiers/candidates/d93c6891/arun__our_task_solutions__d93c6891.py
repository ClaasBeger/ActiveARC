"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: d93c6891
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__d93c6891
"""
from __future__ import annotations



import numpy as np

def solve_d93c6891(input_grid):
    """
    Concepts: Filling 7-blocks using available 5s attached in the direction opposite to the wall of 0s.

    Transformation steps:
    1. Extract connected components, ignoring 0s and 4s.
    2. For each component:
       - Identify bounding box of 7-blocks and count attached 5s.
       - Fill the 7-block with 5s in the direction opposite to the wall of 0s.
       - Change original 5s to 4s.
    """
    from grid_utils import group_connected_positions

    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()

    # Find positions not 0 or 4
    positions = np.argwhere((input_grid != 0) & (input_grid != 4))
    parts = group_connected_positions(positions)

    for part in parts:
        part = np.array(part)
        pos_with_7s = [p for p in part if input_grid[tuple(p)] == 7]
        pos_with_5s = [p for p in part if input_grid[tuple(p)] == 5]
        pos_with_7s = np.array(pos_with_7s)
        pos_with_5s = np.array(pos_with_5s)
        num_5s = len(pos_with_5s)

        if pos_with_7s.size == 0:
            continue

        min_row, min_col = np.min(pos_with_7s, axis=0)
        max_row, max_col = np.max(pos_with_7s, axis=0)

        # Fill direction logic
        if min_row > 0 and np.all(input_grid[min_row-1, min_col:max_col+1] == 0):
            counter = 0
            for r in range(min_row, max_row + 1):
                for c in range(min_col, max_col + 1):
                    if counter < num_5s:
                        output_grid[r, c] = 5
                        counter += 1
        elif max_row < input_grid.shape[0] - 1 and np.all(input_grid[max_row+1, min_col:max_col+1] == 0):
            counter = 0
            for r in range(max_row, min_row - 1, -1):
                for c in range(min_col, max_col + 1):
                    if counter < num_5s:
                        output_grid[r, c] = 5
                        counter += 1
        elif min_col > 0 and np.all(input_grid[min_row:max_row+1, min_col-1] == 0):
            counter = 0
            for c in range(min_col, max_col + 1):
                for r in range(min_row, max_row + 1):
                    if counter < num_5s:
                        output_grid[r, c] = 5
                        counter += 1
        elif max_col < input_grid.shape[1] - 1 and np.all(input_grid[min_row:max_row+1, max_col+1] == 0):
            counter = 0
            for c in range(max_col, min_col - 1, -1):
                for r in range(min_row, max_row + 1):
                    if counter < num_5s:
                        output_grid[r, c] = 5
                        counter += 1

        # Change original 5s to 4s
        if num_5s > 0 and pos_with_5s.size > 0:
            output_grid[pos_with_5s[:, 0], pos_with_5s[:, 1]] = 4

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_d93c6891(input_grid)
    return _result
