"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 12997ef3
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[26](id=26)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0026__12997ef3
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    # Find blue (1) positions
    blue_pos = [(i, j) for i in range(rows) for j in range(cols) if grid[i][j] == 1]
    if not blue_pos:
        return []

    min_r = min(r for r, _ in blue_pos)
    max_r = max(r for r, _ in blue_pos)
    min_c = min(c for _, c in blue_pos)
    max_c = max(c for _, c in blue_pos)
    h = max_r - min_r + 1
    w = max_c - min_c + 1

    # Find single cells (color != 0 and != 1)
    singles = [(i, j, grid[i][j]) for i in range(rows) for j in range(cols) if grid[i][j] != 0 and grid[i][j] != 1]

    # Determine direction
    all_cols = {j for _, j, _ in singles}
    all_rows = {i for i, _, _ in singles}
    if len(all_cols) == 1:
        direction = 'vertical'
        singles.sort(key=lambda x: x[0])  # sort by row
    elif len(all_rows) == 1:
        direction = 'horizontal'
        singles.sort(key=lambda x: x[1])  # sort by col
    else:
        raise ValueError("Singles not aligned vertically or horizontally")

    num = len(singles)

    if direction == 'vertical':
        out_h = h * num
        out_w = w
        output = [[0] * out_w for _ in range(out_h)]
        for idx, (_, _, color) in enumerate(singles):
            for i in range(h):
                for j in range(w):
                    if grid[min_r + i][min_c + j] == 1:
                        output[idx * h + i][j] = color
    else:  # horizontal
        out_h = h
        out_w = w * num
        output = [[0] * out_w for _ in range(out_h)]
        for idx, (_, _, color) in enumerate(singles):
            for i in range(h):
                for j in range(w):
                    if grid[min_r + i][min_c + j] == 1:
                        output[i][idx * w + j] = color

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
