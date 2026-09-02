"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 642248e4
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[206](id=206)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0206__642248e4
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = [row[:] for row in grid]
    rows = len(grid)
    cols = len(grid[0])

    # Check for horizontal bars (top and bottom)
    top_color = grid[0][0] if all(x == grid[0][0] != 0 for x in grid[0]) else None
    bottom_color = grid[rows - 1][0] if all(x == grid[rows - 1][0] != 0 for x in grid[rows - 1]) else None
    if top_color is not None and bottom_color is not None and top_color != bottom_color:
        bar_top = 0
        bar_bottom = rows - 1
        space_start = 1
        space_end = rows - 2
        for c in range(cols):
            blue_rows = [r for r in range(space_start, space_end + 1) if grid[r][c] == 1]
            if not blue_rows:
                continue
            topmost = min(blue_rows)
            dist_top = topmost - bar_top
            dist_bottom = bar_bottom - topmost
            if dist_top < dist_bottom:
                add_r = topmost - 1
                if space_start <= add_r <= space_end:
                    grid[add_r][c] = top_color
            bottommost = max(blue_rows)
            dist_bottom = bar_bottom - bottommost
            dist_top = bottommost - bar_top
            if dist_bottom < dist_top:
                add_r = bottommost + 1
                if space_start <= add_r <= space_end:
                    grid[add_r][c] = bottom_color
        return grid

    # Check for vertical bars (left and right)
    left_color = grid[0][0] if all(grid[r][0] == grid[0][0] != 0 for r in range(rows)) else None
    right_color = grid[0][cols - 1] if all(grid[r][cols - 1] == grid[0][cols - 1] != 0 for r in range(rows)) else None
    if left_color is not None and right_color is not None and left_color != right_color:
        bar_left = 0
        bar_right = cols - 1
        space_start = 1
        space_end = cols - 2
        for r in range(rows):
            blue_cols = [c for c in range(space_start, space_end + 1) if grid[r][c] == 1]
            if not blue_cols:
                continue
            leftmost = min(blue_cols)
            dist_left = leftmost - bar_left
            dist_right = bar_right - leftmost
            if dist_left < dist_right:
                add_c = leftmost - 1
                if space_start <= add_c <= space_end:
                    grid[r][add_c] = left_color
            rightmost = max(blue_cols)
            dist_right = bar_right - rightmost
            dist_left = rightmost - bar_left
            if dist_right < dist_left:
                add_c = rightmost + 1
                if space_start <= add_c <= space_end:
                    grid[r][add_c] = right_color
        return grid

    # If no bars detected, return unchanged
    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
