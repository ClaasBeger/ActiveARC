"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9b365c51
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[326](id=326)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0326__9b365c51
"""
from __future__ import annotations



import numpy as np

def transform(grid_lst: list[list[int]]) -> list[list[int]]:
    if not grid_lst or not grid_lst[0]:
        return []
    grid = [row[:] for row in grid_lst]
    height = len(grid)
    width = len(grid[0])
    # Collect bar colors
    colors = []
    for c in range(width):
        val = grid[0][c]
        if val == 0 or val == 8:
            continue
        is_bar = all(grid[r][c] == val for r in range(height))
        if is_bar:
            colors.append(val)
    # Find groups
    groups = []
    c = 0
    while c < width:
        positions = [r for r in range(height) if grid[r][c] == 8]
        if not positions:
            c += 1
            continue
        min_r = min(positions)
        max_r = max(positions)
        group_cols = [c]
        c += 1
        while c < width:
            pos_next = [r for r in range(height) if grid[r][c] == 8]
            if not pos_next:
                break
            min_next = min(pos_next)
            max_next = max(pos_next)
            if min_next != min_r or max_next != max_r:
                break
            group_cols.append(c)
            c += 1
        groups.append((min_r, max_r, group_cols))
    # Create output
    output = [[0 for _ in range(width)] for _ in range(height)]
    for i, (min_r, max_r, cols) in enumerate(groups):
        if i >= len(colors):
            break  # In case more groups than colors, but examples match
        color = colors[i]
        for col in cols:
            for r in range(height):
                if grid[r][col] == 8:
                    output[r][col] = color
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
