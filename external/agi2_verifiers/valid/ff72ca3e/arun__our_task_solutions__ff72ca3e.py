"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ff72ca3e
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__ff72ca3e
"""
from __future__ import annotations



import numpy as np

def solve_ff72ca3e(input_grid):
    """
    Concepts: BFS region growth, obstacle blocking.

    Breadth-First Search (BFS) — it’s a graph traversal algorithm.
    In simple terms:
    You start at a point (like your 4 cell).
    You visit all the neighbors at distance 1 first,
    Then all neighbors at distance 2,
    And so on — layer by layer.

    It’s like dropping a pebble in water — the ripples expand outward evenly,

    Transformation steps:
    1. For each cell containing the value 4, expand outward.
    2. Mark expansion cells with the value 2 until a cell containing 5 is reached, which blocks further growth.
    """
    # Convert input to a NumPy array and initialize variables
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()


    # Step 1: Find all positions containing the value 4
    positions_with_4 = np.argwhere(input_grid == 4)

    # Process each position containing 4
    for pos in positions_with_4:
        row, col = tuple(pos)

        # Expand outward from the current position
        for radius in range(1, max(nrows, ncols)):
            min_row, max_row = row - radius, row + radius
            min_col, max_col = col - radius, col + radius

            # Check bounds and ensure no blocking cell (value 5) is within the expansion area
            if (
                0 <= min_row < nrows and 0 <= min_col < ncols and
                0 <= max_row < nrows and 0 <= max_col < ncols and
                not np.any(input_grid[min_row:max_row + 1, min_col:max_col + 1] == 5)
            ):
                # Collect positions to mark in the current expansion radius
                pad_positions = set()
                for c in [min_col, max_col]:
                    pad_positions.update((r, c) for r in range(min_row, max_row + 1))
                for r in [min_row, max_row]:
                    pad_positions.update((r, c) for c in range(min_col, max_col + 1))

                # Step 2: Mark the positions with the value 2
                for r, c in pad_positions:
                    output_grid[r, c] = 2
            else:
                # Stop expansion if bounds are exceeded or a blocking cell is encountered
                break

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_ff72ca3e(input_grid)
    return _result
