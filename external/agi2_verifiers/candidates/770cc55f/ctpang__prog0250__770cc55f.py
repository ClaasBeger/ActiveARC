"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 770cc55f
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[250](id=250)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0250__770cc55f
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = [row[:] for row in grid]
    rows = len(grid)
    cols = len(grid[0])

    # Find red_row
    red_row = None
    for r in range(rows):
        if any(grid[r][c] == 2 for c in range(cols)):
            red_row = r
            break  # Assume only one

    if red_row is None:
        return grid

    # Find colored rows (non-zero, non-2)
    colored_rows = []
    for r in range(rows):
        if r != red_row and any(grid[r][c] != 0 for c in range(cols)):
            colored_rows.append(r)

    if len(colored_rows) != 2:
        return grid  # Assume exactly two

    top_row = min(colored_rows)
    bottom_row = max(colored_rows)

    # Get columns sets
    set_top = set(c for c in range(cols) if grid[top_row][c] != 0)
    set_bottom = set(c for c in range(cols) if grid[bottom_row][c] != 0)

    overlap = set_top & set_bottom
    if not overlap:
        return grid

    min_col = min(overlap)
    max_col = max(overlap)

    len_top = len(set_top)
    len_bottom = len(set_bottom)

    if len_top == len_bottom:
        return grid  # No fill if equal, though not in examples

    if len_top > len_bottom:
        height = red_row - top_row - 1
        start_r = top_row + 1
    else:
        height = bottom_row - red_row - 1
        start_r = red_row + 1

    # Fill
    for dr in range(height):
        r = start_r + dr
        for c in range(min_col, max_col + 1):
            grid[r][c] = 4

    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
