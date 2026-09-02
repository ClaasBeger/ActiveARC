"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 4a1cacc2
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[151](id=151)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0151__4a1cacc2
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid:
        return grid
    height = len(grid)
    width = len(grid[0])
    # Find the special cell
    r_spec, c_spec, C = -1, -1, -1
    for r in range(height):
        for c in range(width):
            if grid[r][c] != 8:
                r_spec = r
                c_spec = c
                C = grid[r][c]
                break  # Assume only one
        if r_spec != -1:
            break
    if r_spec == -1:
        return [row[:] for row in grid]
    # Rows
    dist_top = r_spec
    dist_bottom = height - 1 - r_spec
    min_dist_row = min(dist_top, dist_bottom)
    if dist_top < dist_bottom or dist_top == dist_bottom:
        # Expand up
        min_r = r_spec - min_dist_row
        max_r = r_spec
    else:
        # Expand down
        min_r = r_spec
        max_r = r_spec + min_dist_row
    # Columns
    dist_left = c_spec
    dist_right = width - 1 - c_spec
    min_dist_col = min(dist_left, dist_right)
    if dist_left < dist_right or dist_left == dist_right:
        # Expand left
        min_c = c_spec - min_dist_col
        max_c = c_spec
    else:
        # Expand right
        min_c = c_spec
        max_c = c_spec + min_dist_col
    # Create output
    output = [row[:] for row in grid]
    for r in range(min_r, max_r + 1):
        for c in range(min_c, max_c + 1):
            output[r][c] = C
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
