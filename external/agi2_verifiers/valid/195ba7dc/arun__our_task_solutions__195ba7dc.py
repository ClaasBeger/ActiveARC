"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 195ba7dc
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__195ba7dc
"""
from __future__ import annotations



import numpy as np

def solve_195ba7dc(input_grid):
    """
    Find a column containing all 2s and create a binary output grid based on merging 
    the regions separated by this column.
    
    Concepts:
    - Column-based partitioning: Identifying a dividing column with value 2
    - Region merging: Combining data from separate regions of the grid
    - Binary transformation: Converting to 1s where either region had non-zero values
    
    Transformation Steps:
    1. Identify the column where all values equal 2 (partition column)
    2. Split the grid into left and right parts, excluding the partition column
    3. Add corresponding elements from both parts
    4. Create a binary output where any non-zero sum becomes 1
    """
    
    # Convert to numpy array
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape

    # Find partitioning column containing all 2s
    col_with_2 = None
    for c in range(ncols):
        if np.all(input_grid[:, c] == 2):
            col_with_2 = c
            break
    
    # Split grid into left and right parts around partition
    left_part = input_grid[:, :col_with_2]
    right_part = input_grid[:, col_with_2+1:]

    # Combine regions and create binary output
    # (1 where either region had a value, 0 where both were 0)
    add = left_part + right_part
    output_grid = (add != 0).astype(int)

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_195ba7dc(input_grid)
    return _result
