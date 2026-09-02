"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ce8d95cc
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[430](id=430)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0430__ce8d95cc
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []

    rows = len(grid)
    cols = len(grid[0])

    # Get vertical columns and colors from row 0
    vert_cols = []
    vert_colors = []
    for c in range(cols):
        if grid[0][c] != 0:
            vert_cols.append(c)
            vert_colors.append(grid[0][c])

    N = len(vert_cols)
    if N == 0:
        return []

    W = 2 * N + 1

    # Find bar rows and colors
    bars = []
    vert_set = set(vert_cols)
    for r in range(rows):
        non_vert_colors = [grid[r][c] for c in range(cols) if c not in vert_set]
        if non_vert_colors:
            s = set(non_vert_colors)
            if len(s) == 1 and list(s)[0] != 0:
                bar_color = list(s)[0]
                bars.append((r, bar_color))

    B = len(bars)
    H = 2 * B + 1

    output = [[0 for _ in range(W)] for _ in range(H)]

    # Set empty rows
    for i in range(H):
        if i % 2 == 0:
            for j in range(1, W, 2):
                m = (j - 1) // 2
                output[i][j] = vert_colors[m]

    # Set bar rows
    for k in range(B):
        out_row = 2 * k + 1
        r, bar_color = bars[k]
        # Even columns: bar_color
        for j in range(0, W, 2):
            output[out_row][j] = bar_color
        # Odd columns: input value at intersection
        for j in range(1, W, 2):
            m = (j - 1) // 2
            vc = vert_cols[m]
            output[out_row][j] = grid[r][vc]

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
