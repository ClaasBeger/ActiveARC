"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 3979b1a8
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[110](id=110)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0110__3979b1a8
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    n = len(grid)
    out = [[0] * (2 * n) for _ in range(2 * n)]

    # copy input to top-left
    for i in range(n):
        for j in range(n):
            out[i][j] = grid[i][j]

    # determine colors
    A = grid[0][0]
    B = grid[n // 2][n // 2]
    C = grid[0][1]
    cycle = [A, B, C]

    # fill top-right vertical bars
    for m in range(n):
        col = n + m
        color_idx = m % 3
        color = cycle[color_idx]
        for i in range(n):
            out[i][col] = color

    # fill bottom rows
    for k in range(n):
        row = n + k
        color_idx = k % 3
        main_color = cycle[color_idx]
        main_len = n + k
        # fill main
        for j in range(main_len):
            out[row][j] = main_color
        remaining = 2 * n - main_len
        if remaining == 0:
            continue
        # next color idx
        next_idx = (color_idx + 1) % 3
        curr_color = cycle[next_idx]
        if remaining == 1:
            out[row][main_len] = curr_color
            continue
        # fill 2 of curr
        for jj in range(2):
            out[row][main_len + jj] = curr_color
        pos = main_len + 2
        remaining -= 2
        while remaining > 0:
            next_idx = (next_idx + 1) % 3
            curr_color = cycle[next_idx]
            out[row][pos] = curr_color
            pos += 1
            remaining -= 1

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
