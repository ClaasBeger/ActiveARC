"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 46c35fc7
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__46c35fc7
"""
from __future__ import annotations



import numpy as np

def solve_46c35fc7(input_grid):
    """
    Concepts: Connected component extraction, block rotation, selective masking.

    Transformation steps:
    1. Identify non-background regions using connected components.
    2. For each 3x3 block, mask and rotate corners and edges separately.
    3. Combine rotated blocks and restore the center value.
    """
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()

    background_val = 7
    positions = np.argwhere(input_grid != background_val)

    from grid_utils import group_connected_positions

    # Group non-background positions into connected components
    parts = group_connected_positions(positions, connectivity=4)
    for part in parts:
        part = np.array(part)
        min_row, min_col = part.min(axis=0)
        max_row, max_col = part.max(axis=0)
        block = output_grid[min_row:max_row + 1, min_col:max_col + 1]

        # Define indices for corners and edges in a 3x3 block
        corner_indices = [(0, 0), (0, 2), (2, 0), (2, 2), (1, 1)]
        edge_indices = [(0, 1), (1, 0), (1, 2), (2, 1), (1, 1)]

        # Mask and rotate corners
        corner_block = block.copy()
        for r, c in edge_indices:
            corner_block[r, c] = 0
        corner_block = np.rot90(corner_block)

        # Mask and rotate edges
        edge_block = block.copy()
        for r, c in corner_indices:
            edge_block[r, c] = 0
        edge_block = np.rot90(edge_block, k=-1)

        # Combine rotated blocks and restore center
        output_block = corner_block + edge_block
        output_block[1, 1] = block[1, 1]

        output_grid[min_row:max_row + 1, min_col:max_col + 1] = output_block

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_46c35fc7(input_grid)
    return _result
