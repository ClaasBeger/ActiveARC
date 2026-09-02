"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 689c358e
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[220](id=220)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0220__689c358e
"""
from __future__ import annotations



import numpy as np

from collections import defaultdict

def transform(grid: list[list[int]]) -> list[list[int]]:
    new_grid = [row[:] for row in grid]
    n = len(grid)
    color_pos = defaultdict(list)
    for i in range(n):
        for j in range(n):
            c = grid[i][j]
            if c != 0 and c != 6 and c != 7:
                color_pos[c].append((i, j))
    for c, pos in color_pos.items():
        if len(pos) < 3:
            continue
        row_count = defaultdict(int)
        col_count = defaultdict(int)
        for r, cc in pos:
            row_count[r] += 1
            col_count[cc] += 1
        cross_row = max(row_count, key=row_count.get)
        cross_col = max(col_count, key=col_count.get)
        # horizontal
        horz_cols = [cc for r, cc in pos if r == cross_row]
        min_j = min(horz_cols)
        max_j = max(horz_cols)
        left_len = cross_col - min_j
        right_len = max_j - cross_col
        if left_len != right_len:
            if left_len > right_len:
                new_grid[cross_row][0] = 0
                new_grid[cross_row][n-1] = c
            else:
                new_grid[cross_row][0] = c
                new_grid[cross_row][n-1] = 0
        # vertical
        vert_rows = [r for r, cc in pos if cc == cross_col]
        min_i = min(vert_rows)
        max_i = max(vert_rows)
        up_len = cross_row - min_i
        down_len = max_i - cross_row
        if up_len != down_len:
            if up_len > down_len:
                new_grid[0][cross_col] = 0
                new_grid[n-1][cross_col] = c
            else:
                new_grid[0][cross_col] = c
                new_grid[n-1][cross_col] = 0
    return new_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
