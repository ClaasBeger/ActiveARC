"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: f83cb3f6
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__f83cb3f6
"""
from __future__ import annotations



import numpy as np

def solve_f83cb3f6(input_grid):
    """
    Concepts: barrier-based sliding, directional movement toward barrier.

    Transformation: Slide all non-zero, non-8 values toward the nearest side of a continuous 8-barrier until adjacent, 
    with any barrier gaps letting them fall off the grid.

    Transformation steps:
    1. Identify whether the barrier (8s) is vertical or horizontal.
    2. For each marked value (≠0, ≠8), slide it toward the nearest side of the barrier
       in its row/column until adjacent to an 8, stopping early if blocked by the grid edge
       or falling off through barrier gaps.
    """
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = np.zeros_like(input_grid)
    
    # Find barrier position
    barrier_pos = np.argwhere(input_grid == 8)

    if len(barrier_pos) == 0:
        return input_grid.copy()

    # Check if barrier is vertical (same col) or horizontal (same row)
    if np.all(barrier_pos[:,1] == barrier_pos[0,1]):
        # Vertical barrier
        barrier_col = barrier_pos[0,1]
        for r in range(nrows):
            if input_grid[r,barrier_col] != 8:  # skip gaps
                continue
            # Move from left
            for c in range(barrier_col-1, -1, -1):
                if input_grid[r,c] != 0 and input_grid[r,c] != 8:
                    output_grid[r,barrier_col-1] = input_grid[r,c]
                # Move from right
            for c in range(barrier_col+1, input_grid.shape[1]):
                if input_grid[r,c] != 0 and input_grid[r,c] != 8:
                    output_grid[r,barrier_col+1] = input_grid[r,c]
        output_grid[input_grid == 8] = 8

    elif np.all(barrier_pos[:,0] == barrier_pos[0,0]):
        # Horizontal barrier
        barrier_row = barrier_pos[0,0]
        for c in range(ncols):
            if input_grid[barrier_row,c] != 8:
                continue
            # Move from above
            for r in range(barrier_row-1, -1, -1):
                if input_grid[r,c] != 0 and input_grid[r,c] != 8:
                    output_grid[barrier_row-1,c] = input_grid[r,c]
            # Move from below
            for r in range(barrier_row+1, input_grid.shape[0]):
                if input_grid[r,c] != 0 and input_grid[r,c] != 8:
                    output_grid[barrier_row+1,c] = input_grid[r,c]
        output_grid[input_grid == 8] = 8

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_f83cb3f6(input_grid)
    return _result
