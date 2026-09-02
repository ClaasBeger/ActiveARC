"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 67c52801
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__67c52801
"""
from __future__ import annotations



import numpy as np

def solve_67c52801(input_grid):
    """
    Rearranges colored blocks from the top part to the bottom part by matching their widths to available (background) spaces.
 
    Concept:
        - Identify colored blocks in the upper part of the grid.
        - Identify contiguous background spaces in the bottom two rows.
        - Place each colored block into a matching-width background space, rotating if necessary.
 
    Steps:
        1. Identify the background color (most frequent).
        2. Find contiguous background spaces in the bottom two rows.
        3. Extract colored blocks from the top rows.
        4. Sort background spaces and blocks by width (descending).
        5. Place each block into a matching-width space, rotating if needed.
    """
    from grid_utils import group_connected_positions
 
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = np.copy(input_grid)
 
    # Identify background color (most frequent)
    unique_colors, counts = np.unique(input_grid, return_counts=True)
    background_color = unique_colors[np.argmax(counts)]
 
    # Find contiguous background spaces in the bottom two rows
    bottom_rows = input_grid[-2:, :]
    pos = np.argwhere(bottom_rows == background_color)
    groups = group_connected_positions(pos)
 
    # Sort background groups by width (descending)
    group_widths = [len(group) for group in groups]
    sorted_indices = np.argsort(-np.array(group_widths))
    groups = [groups[i] for i in sorted_indices]
 
    # Extract colored blocks from the top rows
    top_rows = input_grid[:-2, :]
    colors = np.unique(top_rows[top_rows != background_color])
    output_grid[:-2, :] = background_color  # Clear top rows
 
    colored_blocks = []
    for color in colors:
        pos = np.argwhere(top_rows == color)
        min_row, min_col = pos.min(axis=0)
        max_row, max_col = pos.max(axis=0)
        block = top_rows[min_row:max_row+1, min_col:max_col+1]
        colored_blocks.append(block)
 
    # Sort blocks by area (descending)
    block_areas = [block.shape[0] * block.shape[1] for block in colored_blocks]
    sorted_block_indices = np.argsort(-np.array(block_areas))
    colored_blocks = [colored_blocks[i] for i in sorted_block_indices]
 
    # Place each block into a matching-width background space
    used_blocks = set()
    for group in groups:
        group = np.array(group) + np.array([nrows - 2, 0])  # Adjust to grid coordinates
        min_col, max_col = group[:, 1].min(), group[:, 1].max()
        group_width = max_col - min_col + 1
 
        for idx, block in enumerate(colored_blocks):
            if idx in used_blocks:
                continue
            for candidate in [block, np.rot90(block)]:
                bh, bw = candidate.shape
                # Only place if block fits exactly in width and fits in the second last row
                if bw == group_width and bh <= 2:
                    row_end = nrows - 1
                    row_start = row_end - bh
                    output_grid[row_start:row_end, min_col:min_col + bw] = candidate
                    used_blocks.add(idx)
                    break
            if idx in used_blocks:
                break
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_67c52801(input_grid)
    return _result
