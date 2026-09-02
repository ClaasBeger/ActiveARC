"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 1d398264
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[47](id=47)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0047__1d398264
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid:
        return grid
    height = len(grid)
    width = len(grid[0])
    output = [row[:] for row in grid]

    # Find the bounding box of the non-zero cells
    non_zero_positions = [(r, c) for r in range(height) for c in range(width) if grid[r][c] != 0]
    if not non_zero_positions:
        return output
    min_row = min(r for r, c in non_zero_positions)
    max_row = max(r for r, c in non_zero_positions)
    min_col = min(c for r, c in non_zero_positions)
    max_col = max(c for r, c in non_zero_positions)

    # Assuming it's 3x3
    if max_row - min_row != 2 or max_col - min_col != 2:
        return output  # Not matching expected structure

    central_row = min_row + 1
    upper_row = min_row
    lower_row = min_row + 2

    # Extend central row horizontally
    left_color = grid[central_row][min_col]
    right_color = grid[central_row][min_col + 2]
    for c in range(min_col):
        output[central_row][c] = left_color
    for c in range(min_col + 3, width):
        output[central_row][c] = right_color

    # Extend upper row upwards
    u_l_color = grid[upper_row][min_col]
    u_m_color = grid[upper_row][min_col + 1]
    u_r_color = grid[upper_row][min_col + 2]
    d = 1
    while True:
        row = upper_row - d
        if row < 0:
            break
        # Left up-left
        col = min_col - d
        if 0 <= col < width:
            output[row][col] = u_l_color
        # Middle up
        col = min_col + 1
        if 0 <= col < width:
            output[row][col] = u_m_color
        # Right up-right
        col = (min_col + 2) + d
        if 0 <= col < width:
            output[row][col] = u_r_color
        d += 1

    # Extend lower row downwards
    l_l_color = grid[lower_row][min_col]
    l_m_color = grid[lower_row][min_col + 1]
    l_r_color = grid[lower_row][min_col + 2]
    d = 1
    while True:
        row = lower_row + d
        if row >= height:
            break
        # Left down-left
        col = min_col - d
        if 0 <= col < width:
            output[row][col] = l_l_color
        # Middle down
        col = min_col + 1
        if 0 <= col < width:
            output[row][col] = l_m_color
        # Right down-right
        col = (min_col + 2) + d
        if 0 <= col < width:
            output[row][col] = l_r_color
        d += 1

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
