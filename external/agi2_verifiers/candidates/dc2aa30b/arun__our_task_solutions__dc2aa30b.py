"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: dc2aa30b
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__dc2aa30b
"""
from __future__ import annotations



import numpy as np

def solve_dc2aa30b(input_grid):
    """
    Rearranges grid blocks based on their content of value 2 from right to left, top to bottom row-wise.
    
    Concepts:
    - Block detection: Identifies grid partitions separated by rows of zeros
    - Content analysis: Counts occurrences of value 2 in each block
    - Spatial reorganization: Rearranges blocks by descending count in right-to-left order
    
    Transformation steps:
    1. Identify grid partitioning by detecting rows of zeros
    2. Extract individual blocks from the partitioned grid
    3. Count occurrences of value 2 in each block
    4. In the output grid, rearrange blocks in descending order of value 2 count from right to left, top to bottom row-wise
    """
    
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = np.zeros_like(input_grid)  # Start with empty grid of same size

    # Identify rows that consist entirely of zeros
    rows_with_0s = []
    for r in range(nrows):
        if np.all(input_grid[r] == 0):
            rows_with_0s.append(r)
    rows_with_0s = np.sort(rows_with_0s)
    
    # Calculate block size from the spacing between zero rows
    size = rows_with_0s[1] - rows_with_0s[0] - 1 if len(rows_with_0s) > 1 else nrows
    
    # Extract blocks and count value 2s in each
    blocks = []
    num_2s = []
    for r in range(0, nrows, size+1):
        for c in range(0, ncols, size+1):
            block = input_grid[r:r+size, c:c+size]
            count_2 = np.sum(block == 2)
            num_2s.append(count_2)
            blocks.append(block)

    # Get sort order for blocks by count of 2s
    order = np.argsort(num_2s)
    num_blocks = len(blocks)
    
    # Reshape order array and flip left-right for right-to-left ordering
    sqrt = int(np.sqrt(num_blocks))
    order = np.fliplr(order.reshape(sqrt, sqrt))
    
    # Place blocks in output grid according to new arrangement
    for i in range(sqrt):
        for j in range(sqrt):
            o = order[i, j]
            start_row = i * (size + 1)
            start_col = j * (size + 1)
            output_grid[start_row:start_row+size, start_col:start_col+size] = blocks[o]
    
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_dc2aa30b(input_grid)
    return _result
