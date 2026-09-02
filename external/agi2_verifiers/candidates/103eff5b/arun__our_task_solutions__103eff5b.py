"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 103eff5b
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__103eff5b
"""
from __future__ import annotations



import numpy as np

def solve_103eff5b(input_grid):
    """
    Concepts:
    - grid rotation, scaling, and pattern matching,
    - color (fill value) in placeholder pattern as per given reference
 
    Steps:
    1. Extract reference pattern (non-zero, non-8 values).
    2. Extract placeholder pattern (pattern of 8s).
    3. Reduce placeholder by removing duplicate rows and columns.
    4. Find correct orientation by rotating reference pattern.
    5. Replace placeholders with scaled reference pattern.
    """
 
    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()
 
    # Extract reference pattern (non-zero, non-8 values)
    reference_positions = np.argwhere((input_grid != 0) & (input_grid != 8))
    min_row, min_col = np.min(reference_positions, axis=0)
    max_row, max_col = np.max(reference_positions, axis=0)
    reference_pattern = input_grid[min_row:max_row+1, min_col:max_col+1]
    reference_mask = reference_pattern != 0
 
    # Extract placeholder pattern (pattern of 8s)
    placeholder_positions = np.argwhere(input_grid == 8)
    min_row_ph, min_col_ph = np.min(placeholder_positions, axis=0)
    max_row_ph, max_col_ph = np.max(placeholder_positions, axis=0)
    placeholder_pattern = input_grid[min_row_ph:max_row_ph+1, min_col_ph:max_col_ph+1]
 
    # Remove consecutive duplicate rows
    row_differences = np.any(placeholder_pattern[1:] != placeholder_pattern[:-1], axis=1)
    unique_rows = np.r_[True, row_differences]
    reduced_pattern = placeholder_pattern[unique_rows]
 
    # Remove consecutive duplicate columns
    col_differences = np.any(reduced_pattern[:, 1:] != reduced_pattern[:, :-1], axis=0)
    unique_cols = np.r_[True, col_differences]
    reduced_pattern = reduced_pattern[:, unique_cols]
   
    # Create mask of placeholder positions
    placeholder_mask = reduced_pattern == 8
 
    # Calculate scaling factor
    scaling_factor = (max_row_ph - min_row_ph + 1) // (max_row - min_row + 1)
 
    # Find correct orientation and replace placeholders
    for rotation in range(4):
        rotated_reference_mask = np.rot90(reference_mask, k=rotation)
        if np.array_equal(rotated_reference_mask, placeholder_mask):
            rotated_reference = np.rot90(reference_pattern, k=rotation)
           
            # Replace each cell in the placeholder with scaled reference cells
            ref_height, ref_width = rotated_reference.shape
            for r in range(ref_height):
                for c in range(ref_width):
                    r_start = min_row_ph + r * scaling_factor
                    r_end = min_row_ph + (r + 1) * scaling_factor
                    c_start = min_col_ph + c * scaling_factor
                    c_end = min_col_ph + (c + 1) * scaling_factor
                    output_grid[r_start:r_end, c_start:c_end] = rotated_reference[r, c]
            break
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_103eff5b(input_grid)
    return _result
