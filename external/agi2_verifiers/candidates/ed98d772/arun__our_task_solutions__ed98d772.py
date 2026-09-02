"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ed98d772
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__ed98d772
"""
from __future__ import annotations



import numpy as np

def solve_ed98d772(input_grid):
    """
    Concepts: Rotate grid, concatenate or stack grids

    Transformation steps:
    1. Generate the 90-degree, 180-degree, 270-degree rotated versions of the input grid.
    2. Concatenate the original grid with the 90-degree rotated version (the top half)
    3. Concatenate the 180-degree rotated version with the 270-degree rotated version (the bottom half).
    4. Concatenate the top and bottom halves to form the final output grid.
    """
    input_grid = np.array(input_grid)

    rotate_90_cc = np.rot90(input_grid, k=1)   # Step 1: Rotate the input grid 90 degrees counterclockwise
    rotate_180_cc = np.rot90(input_grid, k=2)  # Step 1: Rotate the input grid 180 degrees counterclockwise
    rotate_270_cc = np.rot90(input_grid, k=3)  # Step 1: Rotate the input grid 270 degrees counterclockwise

    # Step 2: Concatenate the original grid with the 90-degree rotated version
    top_half = np.hstack([input_grid, rotate_90_cc])
    bottom_half = np.hstack([rotate_180_cc, rotate_270_cc ])
    output_grid = np.vstack([top_half, bottom_half])

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_ed98d772(input_grid)
    return _result
