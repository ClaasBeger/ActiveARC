"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 278e5215
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__278e5215
"""
from __future__ import annotations



import numpy as np

def solve_278e5215(input_grid):
    """
    Concept: Subgrid extraction and column-wise filling based on a reference block.

    Transformation Steps:
    1. Extract the bounding box containing all 5s (defines the output region).
    2. Identify the minimal block of non-5, non-0 values (used for fill colors).
    3. Use the bottom row of this block as the background reference.
    4. For each column in the cropped 5-region, fill with the common value from the corresponding column in the block,
    5. Replace all positions of 0s inside the cropped 5-region with the background value.
    """

    input_grid = np.array(input_grid)

    # 1. Bounding box of 5s
    pos_with_5 = np.argwhere(input_grid == 5)
    min_row_5, min_col_5 = pos_with_5.min(axis=0)
    max_row_5, max_col_5 = pos_with_5.max(axis=0)
    output_grid = input_grid[min_row_5:max_row_5+1, min_col_5:max_col_5+1].copy()
    pos_0 = np.argwhere(output_grid == 0)

    # 2. Bounding box of non-5, non-0 block
    positions = np.argwhere((input_grid != 5) & (input_grid != 0))
    min_row, min_col = positions.min(axis=0)
    max_row, max_col = positions.max(axis=0)
    block = input_grid[min_row:max_row+1, min_col:max_col+1]

    # 3. Background value (color) reference from bottom row
    background = np.unique(block[-1, :])[0]
    top_part = block[:-1, :]

    # 4. Fill columns in cropped 5-region
    for c in range(top_part.shape[1]):
        val = np.unique(top_part[:, c])[0]
        output_grid[:, c] = val

    # 5. Replace all positions of zeros (old background) with new background value
    output_grid[pos_0[:, 0], pos_0[:, 1]] = background

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_278e5215(input_grid)
    return _result
