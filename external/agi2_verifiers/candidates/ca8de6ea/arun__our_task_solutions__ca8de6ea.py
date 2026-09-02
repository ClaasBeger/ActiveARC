"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ca8de6ea
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__ca8de6ea
"""
from __future__ import annotations



import numpy as np

def solve_ca8de6ea(input_grid):
    """
    Transform grid by extracting inner content and swapping corner and adjacent values.
    
    Concepts:
    - Grid transformation: Extracting inner region while preserving corners
    - Pattern manipulation: Moving values between specific positions
    - Corner preservation: Maintaining original corner values

    Transformation Steps:
    1. Extract the inner block of the grid (all but outer border)
    2. For each corner position, copy its value to the adjacent cross position
    3. Replace corner values with those from the original grid
    """
    
    # Convert to numpy array
    input_grid = np.array(input_grid)

    # Extract the center block (remove border)
    center_block = input_grid[1:-1, 1:-1]
    output_grid = center_block

    # Define relative positions of corners and adjacent cross positions
    corners = [(0, 0), (0, -1), (-1, 0), (-1, -1)]  # Top-left, top-right, bottom-left, bottom-right
    cross = [(0, 1), (1, 0), (1, -1), (-1, 1)]      # Right of TL, below TL, left of BR, above BR

    # For each pair of positions, copy corner values to cross positions
    # and restore original corner values
    for i in range(4):
        # Copy corner value to adjacent cross position
        output_grid[cross[i]] = output_grid[corners[i]]
        # Restore original corner value from input grid
        output_grid[corners[i]] = input_grid[corners[i]]

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_ca8de6ea(input_grid)
    return _result
