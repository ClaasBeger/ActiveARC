"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 37ce87bb
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__37ce87bb
"""
from __future__ import annotations



import numpy as np

def solve_37ce87bb(input_grid):
    """
    Concepts: Counting and marking based on cell values.

    Steps:
    1. Count the number of cells with value 8 and value 2.
    2. Compute the difference (num_5s = num_8s - num_2s).
    3. Fill the last 'num_5s' rows in the second-to-last column with 5.
    """

    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()

    # Step 1: Find positions of 8s and 2s
    pos_with_8 = np.argwhere(input_grid == 8)
    pos_with_2 = np.argwhere(input_grid == 2)

    # Step 2: Count occurrences
    num_8s = pos_with_8.shape[0]
    num_2s = pos_with_2.shape[0]

    # Step 3: Compute number of 5s to fill
    num_5s = num_8s - num_2s

    # Step 4: Fill the last 'num_5s' rows in the second-to-last column with 5
    if num_5s > 0:
        output_grid[-num_5s:, -2] = 5

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_37ce87bb(input_grid)
    return _result
