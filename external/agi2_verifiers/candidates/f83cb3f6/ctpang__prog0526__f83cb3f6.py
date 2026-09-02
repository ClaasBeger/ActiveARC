"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: f83cb3f6
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[526](id=526)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0526__f83cb3f6
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    height = len(grid)
    width = len(grid[0])
    # Find purple positions
    purple_pos = [(r, c) for r in range(height) for c in range(width) if grid[r][c] == 8]
    if not purple_pos:
        return [row[:] for row in grid]
    rows_with_8 = set(r for r, c in purple_pos)
    cols_with_8 = set(c for r, c in purple_pos)
    is_horizontal = len(rows_with_8) == 1
    is_vertical = len(cols_with_8) == 1
    if not (is_horizontal or is_vertical):
        return [row[:] for row in grid]  # Not handling non-straight
    # Find C
    colors = set()
    for r in range(height):
        for c in range(width):
            if grid[r][c] != 0 and grid[r][c] != 8:
                colors.add(grid[r][c])
    if len(colors) != 1:
        return [row[:] for row in grid]  # Not handling multiple colors
    C = colors.pop()
    # Create output
    output = [row[:] for row in grid]
    # Remove all C
    for r in range(height):
        for c in range(width):
            if output[r][c] == C:
                output[r][c] = 0
    if is_horizontal:
        purple_row = next(iter(rows_with_8))
        for j in range(width):
            if grid[purple_row][j] == 8:
                # Above
                has_above = any(grid[r][j] == C for r in range(purple_row))
                if has_above and purple_row - 1 >= 0:
                    output[purple_row - 1][j] = C
                # Below
                has_below = any(grid[r][j] == C for r in range(purple_row + 1, height))
                if has_below and purple_row + 1 < height:
                    output[purple_row + 1][j] = C
    elif is_vertical:
        purple_col = next(iter(cols_with_8))
        for i in range(height):
            if grid[i][purple_col] == 8:
                # Left
                has_left = any(grid[i][c] == C for c in range(purple_col))
                if has_left and purple_col - 1 >= 0:
                    output[i][purple_col - 1] = C
                # Right
                has_right = any(grid[i][c] == C for c in range(purple_col + 1, width))
                if has_right and purple_col + 1 < width:
                    output[i][purple_col + 1] = C
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
