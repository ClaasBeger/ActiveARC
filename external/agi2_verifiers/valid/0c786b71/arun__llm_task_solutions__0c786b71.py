"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 0c786b71
source: ArunSehrawat/arc-agi2-solutions:llm
original_path: llm_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__llm_task_solutions__0c786b71
"""
from __future__ import annotations



import numpy as np

def solve_0c786b71(input_grid):
    """
    Concepts: dihedral kaleidoscope, rotation, reflection

    Transformation steps:
    1. Place rot180(input) in the top-left quadrant.
    2. Place flipud(input) top-right, fliplr(input) bottom-left, and the original bottom-right.
    """
    input_grid = np.array(input_grid)
    top_half = np.hstack([np.rot90(input_grid, 2), np.flipud(input_grid)])  # Step 1–2: top quadrants
    bottom_half = np.hstack([np.fliplr(input_grid), input_grid])             # Step 2: bottom quadrants
    output_grid = np.vstack([top_half, bottom_half])
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_0c786b71(input_grid)
    return _result
