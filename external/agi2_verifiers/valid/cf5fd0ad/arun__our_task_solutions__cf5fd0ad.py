"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: cf5fd0ad
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__cf5fd0ad
"""
from __future__ import annotations



import numpy as np

def solve_cf5fd0ad(input_grid):
    """
    Concepts: duplication, rotation, and stacking of blocks.

    Transformation steps:
    1. Duplicate the input grid to form a larger block (bottom-right).
    2. Rotate this block to create top-right, top-left, and bottom-left blocks.
    3. Assemble the four blocks into a new grid by stacking and concatenation.
    """

    input_grid = np.array(input_grid)
    # Step 1: Create the bottom-right block by duplicating the input grid
    bottom_right_block = np.vstack([
        np.hstack([input_grid, input_grid]),
        np.hstack([input_grid, input_grid])
    ])

    # Step 2: Generate rotated blocks for other corners
    top_right_block = np.rot90(bottom_right_block, k=-1)
    top_left_block = np.rot90(bottom_right_block, k=-2)
    bottom_left_block = np.rot90(bottom_right_block, k=1)

    # Step 3: Assemble the final output grid
    output_grid = np.vstack([
        np.hstack([top_left_block, top_right_block]),
        np.hstack([bottom_left_block, bottom_right_block])
    ])

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_cf5fd0ad(input_grid)
    return _result
