"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 59341089
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__59341089
"""
from __future__ import annotations



import numpy as np

def solve_59341089(input_grid):
    """
    Concepts: Flip grid, repeat parts, stack grids

    Transformation steps:
    1. Flip the input grid left to right.
    2. Concatenate the flipped grid and the original grid horizontally and get the output part.
    3. Horizontally stack the output part with itself to form the final output grid.
    """
    input_grid = np.array(input_grid)
    
    # Step 1: Flip the input grid left to right
    flipped_lr = np.fliplr(input_grid)
    
    # Step 2: Concatenate the flipped grid and the original grid horizontally to get the output part
    output_part = np.hstack([flipped_lr, input_grid])

    # Step 3: Horizontally stack the output part with itself to form the final output grid
    output_grid = np.hstack([output_part, output_part])
    
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_59341089(input_grid)
    return _result
