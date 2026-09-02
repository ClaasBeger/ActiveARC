"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 342ae2ed
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__342ae2ed
"""
from __future__ import annotations



import numpy as np

def solve_342ae2ed(input_grid):
    """
    Connects two same-color blocks by drawing a diagonal line between their nearest corners.
 
    Concept:
        - For each non-background color, find all connected groups (expecting exactly two).
        - If there are exactly two groups, connect their bounding box corners with a diagonal line.
 
    Transformation Steps:
        1. Identify background and non-background colors.
        2. For each non-background color, find connected groups (blocks)
        3. If there are exactly two blocks, compute their bounding box corners.
        4. Draw a diagonal line between the appropriate corners.
 
    """
    from grid_utils import group_connected_positions
 
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()
 
    unique_colors, counts = np.unique(input_grid, return_counts=True)
    background_color = unique_colors[np.argmax(counts)]
    non_bg_colors = unique_colors[unique_colors != background_color]
 
    for color in non_bg_colors:
        positions = np.argwhere(input_grid == color)
        if len(positions) == 0:
            continue
        groups = group_connected_positions(positions)
        if len(groups) != 2: # expect exactly two block per color to connect
            continue
 
        # Get bounding box corners for both groups
        corners = []
        for group in groups:
            group = np.array(group)
            min_row, min_col = group.min(axis=0)
            max_row, max_col = group.max(axis=0)
            corners.append((min_row, min_col, max_row, max_col))
 
        (r1_min, c1_min, r1_max, c1_max), (r2_min, c2_min, r2_max, c2_max) = corners
 
        # Determine which diagonal to draw
        if r1_min < r2_min and c1_min < c2_min:
            # Top-left to bottom-right
            for step in range(1, min(r2_min - r1_max, c2_min - c1_max) + 1):
                r, c = r1_max + step, c1_max + step
                if r > r2_min or c > c2_min:
                    break
                output_grid[r, c] = color
        elif r1_min > r2_min and c1_min > c2_min:
            # Bottom-right to top-left
            for step in range(1, min(r1_min - r2_max, c1_min - c2_max) + 1):
                r, c = r1_min - step, c1_min - step
                if r < r2_max or c < c2_max:
                    break
                output_grid[r, c] = color
        elif r1_min > r2_min and c1_min < c2_min:
            # Bottom-left to top-right
            for step in range(1, min(r1_min - r2_max, c2_min - c1_max) + 1):
                r, c = r1_min - step, c1_max + step
                if r < r2_max or c > c2_min:
                    break
                output_grid[r, c] = color
        elif r1_min < r2_min and c1_min > c2_min:
            # Top-right to bottom-left
            for step in range(1, min(r2_min - r1_max, c1_min - c2_max) + 1):
                r, c = r1_max + step, c1_min - step
                if r > r2_min or c < c2_max:
                    break
                output_grid[r, c] = color
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_342ae2ed(input_grid)
    return _result
