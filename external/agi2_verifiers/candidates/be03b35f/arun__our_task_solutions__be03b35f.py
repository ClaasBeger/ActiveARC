"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: be03b35f
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__be03b35f
"""
from __future__ import annotations



import numpy as np

def solve_be03b35f(input_grid):
    """
    Concepts: 2x2 grid extraction, 2D 90 degree rotation, pattern matching

    Transformation steps:
    1. Extract 2x2 grids from three corners: top-left, top-right, and bottom-left 
    2. Select TL as the base and generate its 90, 180, and 270 degree rotations
    3. Find which rotations match TR and BL
    4. The unmatched rotation is the output
    """
    input_grid = np.array(input_grid)

    # Step 1: Extract 2x2 corners
    top_left = input_grid[0:2, 0:2]
    top_right = input_grid[0:2, 3:5]
    bottom_left = input_grid[3:5, 0:2]
    two_corners = [top_right, bottom_left]

    # Step 2: Generate all rotations of TL
    rotations = [np.rot90(top_left, k) for k in [1, 2, 3]]

    # Step 3: Identify which rotation is NOT in [TR, BL]
    for rot in rotations:
        if not any(np.array_equal(rot, c) for c in two_corners):
            output_grid = rot
            break

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_be03b35f(input_grid)
    return _result
