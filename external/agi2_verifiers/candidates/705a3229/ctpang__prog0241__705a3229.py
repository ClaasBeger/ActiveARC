"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 705a3229
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[241](id=241)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0241__705a3229
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    rows = len(grid)
    cols = len(grid[0])
    output = [[0 for _ in range(cols)] for _ in range(rows)]
    mid_row = (rows - 1) // 2
    mid_col = (cols - 1) // 2
    for r in range(rows):
        for c in range(cols):
            k = grid[r][c]
            if k == 0:
                continue
            # Vertical
            if r <= mid_row:
                v_len = r + 1
                v_start = r - (v_len - 1)
                v_end = r
            else:
                v_len = rows - r
                v_start = r
                v_end = r + (v_len - 1)
            # Horizontal
            if c <= mid_col:
                h_len = c + 1
                h_start = c - (h_len - 1)
                h_end = c
            else:
                h_len = cols - c
                h_start = c
                h_end = c + (h_len - 1)
            # Fill vertical
            for rr in range(v_start, v_end + 1):
                output[rr][c] = k
            # Fill horizontal
            for cc in range(h_start, h_end + 1):
                output[r][cc] = k
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
