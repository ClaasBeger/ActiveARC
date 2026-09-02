"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 337b420f
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__337b420f
"""
from __future__ import annotations



import numpy as np

def solve_337b420f(input_grid):
    """
    Concept:
        The function extracts the largest connected group of non-background cells from each block of the input grid,
        where blocks are separated by columns of all zeros.
        It then places these groups into a compact output grid, shifting left if needed to avoid overlap.
 
    Transformation Steps:
        1. Identify columns in the input grid that are entirely zeros to use as block separators.
        2. Set the output grid size based on the first partitioning column.
        3. For each block between partitioning columns:
            a. Find all non-background cell positions.
            b. Group these positions by 4-connectivity.
            c. Select the largest group.
            d. Place the group in the output grid at its original positions if free space (with background color 8) is available;
            otherwise, shift left by one column and place.
        4. Return the resulting compact output grid.
    """
 
    from grid_utils import group_connected_positions
 
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
 
    # Get unique colors and their counts
    unique, counts = np.unique(input_grid, return_counts=True)
    background_color = unique[np.argmax(counts)]
 
    # Find columns that are all zeros (partitioning columns)
    partitioning_cols = []
    for c in range(ncols):
        if np.all(input_grid[:, c] == 0):
            partitioning_cols.append(c)
 
    # Set output grid size based on first partitioning column
    H = W = partitioning_cols[0]
    output_grid = np.full((H, W), background_color, dtype=int)
 
    # Add boundaries for block extraction
    partitioning_cols = [-1] + partitioning_cols + [ncols]
 
    # Process each block
    for i in range(len(partitioning_cols) - 1):
        block = input_grid[:, partitioning_cols[i] + 1:partitioning_cols[i + 1]]
        pos = np.argwhere(block != background_color)
        if len(pos) == 0:
            continue
        groups = group_connected_positions(pos, connectivity=4)
        val = block[tuple(pos[0])]
 
        # Find the largest group
        marked_group = None
        size = 0
        for group in groups:
            if len(group) > size:
                size = len(group)
                marked_group = group
        marked_group = np.array(marked_group)
       
        # Place the group in the output grid, shift left if needed
        if np.all(output_grid[marked_group[:, 0], marked_group[:, 1]] == background_color):
            output_grid[marked_group[:, 0], marked_group[:, 1]] = val
        else:
            output_grid[marked_group[:, 0], marked_group[:, 1] - 1] = val
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_337b420f(input_grid)
    return _result
