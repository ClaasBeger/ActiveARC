"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: c48954c1
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__c48954c1
"""
from __future__ import annotations



import numpy as np

def solve_c48954c1(input_grid):
    """
    Unfolding Symmetric Pattern
    Creates a symmetric pattern by mirroring the input grid in multiple directions.
    
    Concepts:
    - Reflective symmetry: Creates horizontal and vertical reflections of the input grid
    - Tiling: Combines the original grid with its reflections to create a larger pattern
    - Self-similarity: Generates a fractal-like structure with the input repeated in a pattern
    
    Transformation steps:
    1. Create a horizontal reflection of the input grid (left-right flip)
    2. Construct a middle row by placing the original grid between two of its horizontal reflections
    3. Create vertical reflections (top-bottom flips) of this middle row
    4. Stack these three rows (reflection, original middle row, reflection) to create a 3x3 tile pattern
    """
    
    input_grid = np.array(input_grid)

    # Step 1: Create horizontal reflection of the grid
    flipped_lr = np.fliplr(input_grid)
    
    # Step 2: Build the middle row by placing the original between two reflections
    middle_stack = np.hstack((flipped_lr, input_grid, flipped_lr))
    
    # Step 3: Create vertical reflections of the middle row
    top_stack = np.flipud(middle_stack)
    bottom_stack = np.flipud(middle_stack)  # Same as top_stack
    
    # Step 4: Stack the three rows vertically to create the final pattern
    output_grid = np.vstack((top_stack, middle_stack, bottom_stack))
    
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_c48954c1(input_grid)
    return _result
