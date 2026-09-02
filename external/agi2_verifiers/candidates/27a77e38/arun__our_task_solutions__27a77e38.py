"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 27a77e38
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__27a77e38
"""
from __future__ import annotations



import numpy as np

def solve_27a77e38(input_grid):
    """
    Place the most frequent value from the top block and put it in the center of the last row.

    Concepts:
    - Grid partitioning
    - Frequency analysis
    - Value placement

    Transformation Steps:
    1. Partition the input grid into top and bottom blocks using the middle row of 5s as a separator.
    2. Find the most frequent value in the top block.
    3. Place this value in the center cell of the last row of the output grid.
    4. Return the modified output grid.
    """
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()

    # Partition grid into top and bottom blocks using the middle row
    top_block = input_grid[:nrows // 2]
    bottom_block = input_grid[(nrows // 2) + 1:]

    # Find the most frequent value in the top block
    unique, counts = np.unique(top_block, return_counts=True)
    most_frequent_value = unique[np.argmax(counts)]

    # Place the most frequent value in the center of the last row
    output_grid[-1, ncols // 2] = most_frequent_value

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_27a77e38(input_grid)
    return _result
