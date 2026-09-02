"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 95a58926
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__95a58926
"""
from __future__ import annotations



import numpy as np

def solve_95a58926(input_grid):
    """
    Transform a grid by removing noise and creating a regular partitioning pattern.
    
    Concepts:
    - Pattern cleaning: Remove noise cells while preserving structural elements
    - Grid partitioning: Create regular grid divisions with horizontal and vertical lines
    - Intersection marking: Place special markers at line intersections
    
    Transformation steps:
    1. Remove noise cells (non 0 and non 5) from the grid
    2. Determine the size of partitioning blocks by finding first line marker
    3. Create regular horizontal and vertical partition lines
    4. Place noise value markers at line intersections

    """

    # Convert input to numpy array and create working copy
    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()
    nrows, ncols = input_grid.shape

    # Constants for grid values (colors)
    BACKGROUND = 0
    PARTITION_LINE = 5

    # Find the noise value (any value that's not background or partition line)
    noise_mask = (input_grid != BACKGROUND) & (input_grid != PARTITION_LINE)
    noise_val = np.unique(input_grid[noise_mask])[0]  # Assume single noise value
    
    # Clean grid by removing noise
    output_grid[output_grid == noise_val] = BACKGROUND

    # Find partition block size by locating first partition line
    block_size = 0
    for size in range(max(nrows, ncols)):
        if np.any(output_grid[:size, :size] == PARTITION_LINE):
            block_size = size
            break

    # Calculate partition line positions
    # Subtract 1 to convert from size to index
    partition_rows = np.array([i*block_size for i in range(1, nrows) 
                             if i*block_size <= nrows]) - 1
    partition_cols = np.array([i*block_size for i in range(1, ncols) 
                             if i*block_size <= ncols]) - 1

    # complete partition grid pattern
    output_grid[partition_rows, :] = PARTITION_LINE  # Horizontal lines
    output_grid[:, partition_cols] = PARTITION_LINE  # Vertical lines

    # Mark intersections with noise value
    for row in partition_rows:
        for col in partition_cols:
            output_grid[row, col] = noise_val

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_95a58926(input_grid)
    return _result
