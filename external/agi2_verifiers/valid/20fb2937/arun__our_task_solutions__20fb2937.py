"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 20fb2937
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__20fb2937
"""
from __future__ import annotations



import numpy as np

def solve_20fb2937(input_grid):
    """
    Concepts: Grid partitioning into rule part (top) and work part (bottom), rule: vale to 3x3 block mapping, in-place replacement.

     Transformation Summary
     a. The input grid is divided into two parts:
        - Top part (before the first full row of 6s): 
          This part provides mapping rules: each rule consists of a 1×1 value and its corresponding 3×3 block (pattern).
        - Bottom part (after the row of 6s): This is where the replacement happens. 
           Each 1×1 value is replaced with its corresponding 3×3 block, as defined in the top part.
     b. The replacement happens in-place in the bottom grid:
        - At each cell in the bottom part: if the value is one of the mapping values, replace it with the corresponding 3×3 block centered at that cell.
        - The output grid is constructed with these replaced blocks (note: blocks can overwrite each other; latest ones persist).

    Transformation steps:
    1. Find the dividing row (partition row full of 6s). The background is represented by 7s.
    2. Extract rule part (top) and work part (bottom)
    3. Get 3 pairs of 3x3 block and value from the rule part.
    4. For each cell in the bottom part of the grid, if it matches a mapped value, replace it with the corresponding 3x3 block centered at that cell.
    5. Construct the output grid with these replacements, ensuring to fill in the background (7s) where no replacements occur.
    """
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    
    # Step 1: Find the dividing row (partition row full of 6s)
    partition_row = np.where(np.all(input_grid == 6, axis=1))[0][0]

    # Step 2: Extract rule part (top) and work part (bottom)
    rule_grid = input_grid[:partition_row]
    work_grid = input_grid[partition_row + 1:]
    
    # Step 3: Get 3 pairs of value and 3x3 block 
    block_to_value_map = {}
    value_to_block_map = {}

    for col in range(0, ncols, 4):  # step by 4: 3x3 block + 1 col gap
        if col + 3 > ncols:
            continue
        block = rule_grid[0:3, col:col+3]
        value = rule_grid[4, col+1]  # center cell in row 4 (value location)
        block_to_value_map[value] = block
        value_to_block_map[value] = block

    # Step 4 and 5: Prepare output grid (same shape as bottom part) and of the background of 7s
    output_grid = np.full_like(work_grid, 7)  

    # Step 4 and 5: Replace values with corresponding 3x3 blocks
    h, w = work_grid.shape
    for r in range(h):
        for c in range(w):
            val = work_grid[r, c]
            if val in value_to_block_map:
                block = value_to_block_map[val]
                for i in range(3):
                    for j in range(3):
                        rr = r + i - 1
                        cc = c + j - 1
                        if 0 <= rr < h and 0 <= cc < w:
                            output_grid[rr, cc] = block[i, j]

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_20fb2937(input_grid)
    return _result
