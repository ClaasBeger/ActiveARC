"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 2753e76c
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__2753e76c
"""
from __future__ import annotations



import numpy as np

def solve_2753e76c(input_grid):
    """
    Create a summary grid showing the number of connected components for each value (color).
    
    Concepts:
    - Connected component analysis: Group adjacent cells with same value
    - Component counting: Track number of distinct connected regions per value
    - Create a summary grid showing the number of connected components for each value (color).
    
    Transformation steps:
    1. Find all non-zero values in the input grid
    2. For each value, count its connected components
    3. Sort values by number of components (descending)
    4. Create output grid where:
       - Each row represents a unique value as per the sorted list
       - Row length equals max number of components for that value
       - Values are right-aligned based on component count
    
    """
    from grid_utils import group_connected_positions


    input_grid = np.array(input_grid)

    # Find all non-zero values
    non_zero_vals = np.unique(input_grid[input_grid != 0])

    # Count connected components for each value
    component_counts = []
    for val in non_zero_vals:
        # Find all positions of current value
        value_positions = np.argwhere(input_grid == val)
        # Group into connected components
        connected_regions = group_connected_positions(value_positions)
        # Store number of components
        component_counts.append(len(connected_regions))

    # Sort values by number of components (descending)
    sort_order = np.argsort(component_counts)[::-1]
    max_components = component_counts[sort_order[0]]

    # Create output grid
    num_values = len(non_zero_vals)
    output_grid = np.zeros((num_values, max_components), dtype=int)

    # Fill output grid with values as per the sorted order, right-aligned by component count
    for row, original_idx in enumerate(sort_order):
        value = non_zero_vals[original_idx]
        count = component_counts[original_idx]
        # Place value in rightmost positions based on component count
        output_grid[row, -count:] = value

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_2753e76c(input_grid)
    return _result
