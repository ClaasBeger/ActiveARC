"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 99306f82
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[319](id=319)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0319__99306f82
"""
from __future__ import annotations



import numpy as np

def transform(grid_lst: list[list[int]]) -> list[list[int]]:
    grid = [row[:] for row in grid_lst]  # Copy the grid
    # Find the chain
    chain = []
    i = 0
    n = len(grid)
    m = len(grid[0]) if grid else 0
    while i < min(n, m) and grid[i][i] != 0 and grid[i][i] != 1:
        chain.append(grid[i][i])
        i += 1
    k = len(chain)
    if k == 0:
        return grid
    # Frame top-left
    row_start = i
    col_start = i
    # Find row_end
    r = row_start
    while r < n and grid[r][col_start] == 1:
        r += 1
    row_end = r - 1
    # Find col_end
    c = col_start
    while c < m and grid[row_start][c] == 1:
        c += 1
    col_end = c - 1
    # Inner area
    i_row_start = row_start + 1
    i_row_end = row_end - 1
    i_col_start = col_start + 1
    i_col_end = col_end - 1
    # Inner dimensions
    h = i_row_end - i_row_start + 1 if i_row_end >= i_row_start else 0
    w = i_col_end - i_col_start + 1 if i_col_end >= i_col_start else 0
    # Fill the inner area
    for row in range(i_row_start, i_row_end + 1):
        for col in range(i_col_start, i_col_end + 1):
            local_r = row - i_row_start
            local_c = col - i_col_start
            dist_top = local_r
            dist_bot = (h - 1) - local_r
            dist_left = local_c
            dist_right = (w - 1) - local_c
            d = min(dist_top, dist_bot, dist_left, dist_right)
            idx = min(d, k - 1)
            grid[row][col] = chain[idx]
    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
