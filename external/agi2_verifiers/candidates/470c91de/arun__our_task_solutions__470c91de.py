"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 470c91de
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__470c91de
"""
from __future__ import annotations



import numpy as np

def solve_470c91de(input_grid):
    """
    Move colored blocks diagonally based on the position of the marker (color 8).
 
    Concept:
        - Extract colored blocks from the input grid.
        - Detect marker positions (color 8) at a block's corner.
        - Move the entire block one step diagonally in the direction of the marker.
 
    Transformation Steps:
        1. Identify the background value (most frequent in the grid).
        2. For each unique value (excluding background and marker 8):
            a. Find the minimal bounding block carrying the value (color).
            b. In the block, find the marker (color 8) position.
            c. Move the block one step diagonally based on the marker's position and remove the marker.
    """
 
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
 
    # Step 1: Find background value
    unique, counts = np.unique(input_grid, return_counts=True)
    background_value = unique[np.argmax(counts)]
    output_grid = np.full((nrows, ncols), background_value, dtype=input_grid.dtype)
 
    marker_color = 8
 
    # Step 2: Select values to process (exclude background and marker)
    selected_vals = unique[(unique != background_value) & (unique != marker_color)]
 
    for val in selected_vals:
        pos_value = np.argwhere(input_grid == val)
        min_row, min_col = pos_value.min(axis=0)
        max_row, max_col = pos_value.max(axis=0)
 
        block = input_grid[min_row:max_row+1, min_col:max_col+1]
        H, W = block.shape
        block_unique, block_counts = np.unique(block, return_counts=True)
        most_frequent_value = block_unique[np.argmax(block_counts)]
 
        # Find marker position (expects only one marker per block)
        marker_positions = np.argwhere(block == marker_color)
        if marker_positions.size == 0:
            continue  # No marker found, skip
        pos_marker = tuple(marker_positions[0])
 
        # Move block diagonally in the direction of the marker and remove the marker
        if pos_marker == (0, 0):  # top-left
            r0, r1 = max(min_row - 1, 0), max_row
            c0, c1 = max(min_col - 1, 0), max_col
            output_grid[r0:r1, c0:c1] = most_frequent_value
        elif pos_marker == (0, W - 1):  # top-right
            r0, r1 = max(min_row - 1, 0), max_row
            c0, c1 = min_col + 1, min(max_col + 2, ncols)
            output_grid[r0:r1, c0:c1] = most_frequent_value
        elif pos_marker == (H - 1, 0):  # bottom-left
            r0, r1 = min_row + 1, min(max_row + 2, nrows)
            c0, c1 = max(min_col - 1, 0), max_col
            output_grid[r0:r1, c0:c1] = most_frequent_value
        elif pos_marker == (H - 1, W - 1):  # bottom-right
            r0, r1 = min_row + 1, min(max_row + 2, nrows)
            c0, c1 = min_col + 1, min(max_col + 2, ncols)
            output_grid[r0:r1, c0:c1] = most_frequent_value
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_470c91de(input_grid)
    return _result
