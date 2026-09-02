"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 7ec998c9
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[261](id=261)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0261__7ec998c9
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []

    height = len(grid)
    width = len(grid[0])

    # Find background and special position
    bg = grid[0][0]
    s_r = None
    s_c = None
    for i in range(height):
        for j in range(width):
            if grid[i][j] != bg:
                if s_r is not None:
                    # Assume only one special cell
                    break
                s_r = i
                s_c = j

    if s_r is None:
        return grid

    new_color = 1

    center = (width - 1) // 2
    reverse = (s_c == center)

    left_count = s_c
    right_count = width - s_c - 1

    # Copy grid
    output = [row[:] for row in grid]

    # Set vertical line
    for i in range(height):
        if i != s_r:
            output[i][s_c] = new_color

    # Set extensions
    top_row = 0
    bottom_row = height - 1

    if reverse:
        # Top: extend right
        for k in range(1, right_count + 1):
            if s_c + k < width:
                output[top_row][s_c + k] = new_color
        # Bottom: extend left
        for k in range(1, left_count + 1):
            if s_c - k >= 0:
                output[bottom_row][s_c - k] = new_color
    else:
        # Top: extend left
        for k in range(1, left_count + 1):
            if s_c - k >= 0:
                output[top_row][s_c - k] = new_color
        # Bottom: extend right
        for k in range(1, right_count + 1):
            if s_c + k < width:
                output[bottom_row][s_c + k] = new_color

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
