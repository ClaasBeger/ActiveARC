"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: b1fc8b8e
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__b1fc8b8e
"""
from __future__ import annotations



import numpy as np

def solve_b1fc8b8e(input_grid):
    """
    Concepts: topology, pattern recognition, pattern extraction, spatial reasoning

    # In the input grid, 8s are either making four 2x2 square or four flipped L shapes.
    # if they are squares, then number of 8s will be 4*4 = 16
    # if they are flipped L, then number of 8s will be 3*4 = 12
    # based on that we can form a 5x5 output grid with four squares or flipped L shapes at the corners.

    Transformation steps:
    1. Initialize a 5x5 output grid with zeros.
    2. Count the number of 8s in the input grid.
    3. If there are 16 8s, they form four squares at the four corners of the output grid.
       If there are 12 8s, they form four flipped L shapes at the four corners of the output grid.
    """
    input_grid = np.array(input_grid)
    # Step 1: Initialize a 5x5 output grid with zeros.
    output_grid = np.zeros((5, 5), dtype=int)

    # In the input grid, 8s are either making four 2x2 square or flipped L shapes.
    # if they are squares, then number of 8s will be 4*4 = 16
    # if they are flipped L, then number of 8s will be 3*4 = 12
    square = np.array([[8, 8], [8, 8]], dtype=int)
    flipped_L = np.array([[0, 8], [8, 8]], dtype=int)
    
    # Step 2: Count the number of 8s in the input grid.
    num_8s = len(np.where(input_grid == 8)[0])

    if num_8s == 16: # Step 3: If there are 16 8s, they form four squares at the four corners of the output grid.
        output_grid[0:2, 0:2] = square   # top-left
        output_grid[0:2, 3:5] = square   # top-right
        output_grid[3:5, 0:2] = square   # bottom-left
        output_grid[3:5, 3:5] = square   # bottom-right
    elif num_8s == 12: # Step 3: If there are 12 8s, they form four flipped L shapes at the four corners of the output grid.
        output_grid[0:2, 0:2] = flipped_L   # top-left
        output_grid[0:2, 3:5] = flipped_L   # top-right
        output_grid[3:5, 0:2] = flipped_L   # bottom-left
        output_grid[3:5, 3:5] = flipped_L   # bottom-right

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_b1fc8b8e(input_grid)
    return _result
