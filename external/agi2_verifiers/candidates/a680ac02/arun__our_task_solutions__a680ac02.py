"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: a680ac02
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__a680ac02
"""
from __future__ import annotations



import numpy as np

def solve_a680ac02(input_grid):
    """
    Identify connected groups of non-zero values, remove solid blocks,
    preserve hollow blocks, trim empty rows/columns, and stack the remaining blocks.
 
    Concept:
    - Connected non-zero regions are either solid (fully filled) or hollow (partially filled).
    - Solid blocks are removed; hollow blocks are extracted and stacked vertically or horizontally
      based on the grid's aspect ratio.
 
    Transformation Steps:
    1. Identify all connected groups of non-zero positions in the input grid.
    2. For each group, remove it if it forms a solid block (all cells non-zero).
    3. Trim the output grid by removing rows and columns that are entirely zero.
    4. Divide the trimmed grid into sections (assuming 4x4 blocks) and extract the bounding box of non-zero positions in each section.
    5. Stack the extracted blocks vertically if the grid is taller than wide, or horizontally otherwise.
    """

    from grid_utils import group_connected_positions
 
    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()
 
    # Find all non-zero positions and group them into connected components
    non_zero_positions = np.argwhere(input_grid != 0)
    connected_groups = group_connected_positions(non_zero_positions)
 
    # Remove solid blocks from output
    for group in connected_groups:
        group = np.array(group)
        min_row, min_col = group.min(axis=0)
        max_row, max_col = group.max(axis=0)
        block = input_grid[min_row:max_row+1, min_col:max_col+1]
        if np.all(block != 0):
            output_grid[min_row:max_row+1, min_col:max_col+1] = 0
 
    # Trim rows and columns that are entirely zero
    non_zero_rows = np.any(output_grid != 0, axis=1)
    non_zero_cols = np.any(output_grid != 0, axis=0)
    output_grid = output_grid[non_zero_rows][:, non_zero_cols]
 
    # Stack hollow blocks
    H, W = output_grid.shape
    block_size = 4
    extracted_blocks = []
 
    if H >= W:
        # Vertical stacking
        for r in range(0, H, block_size):
            section = output_grid[r:r+block_size, :]
            section_positions = np.argwhere(section != 0)
            if len(section_positions) > 0:
                min_r, min_c = section_positions.min(axis=0)
                max_r, max_c = section_positions.max(axis=0)
                block = section[min_r:max_r+1, min_c:max_c+1]
                extracted_blocks.append(block)
        if extracted_blocks:
            output_grid = np.vstack(extracted_blocks)
    else:
        # Horizontal stacking
        for c in range(0, W, block_size):
            section = output_grid[:, c:c+block_size]
            section_positions = np.argwhere(section != 0)
            if len(section_positions) > 0:
                min_r, min_c = section_positions.min(axis=0)
                max_r, max_c = section_positions.max(axis=0)
                block = section[min_r:max_r+1, min_c:max_c+1]
                extracted_blocks.append(block)
        if extracted_blocks:
            output_grid = np.hstack(extracted_blocks)
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_a680ac02(input_grid)
    return _result
