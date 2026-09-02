"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 4852f2fa
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[144](id=144)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0144__4852f2fa
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    # Find purple positions and count yellows
    pos = []
    num_yellow = 0
    rows = len(grid)
    cols = len(grid[0])
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 8:
                pos.append((r, c))
            elif grid[r][c] == 4:
                num_yellow += 1

    if not pos:
        return [[], [], []]  # Empty case, but assume not

    min_r = min(r for r, c in pos)
    max_r = max(r for r, c in pos)
    min_c = min(c for r, c in pos)
    max_c = max(c for r, c in pos)

    bb_h = max_r - min_r + 1
    bb_w = max_c - min_c + 1

    pat_h = 3
    pat_w = 3
    pattern = [[0] * pat_w for _ in range(pat_h)]

    start_r = pat_h - bb_h
    start_c = 0
    for i in range(bb_h):
        for j in range(bb_w):
            val = grid[min_r + i][min_c + j]
            pattern[start_r + i][start_c + j] = val if val == 8 else 0

    # Replicate
    out_w = pat_w * num_yellow
    output = [[0] * out_w for _ in range(pat_h)]
    for k in range(num_yellow):
        for r in range(pat_h):
            for j in range(pat_w):
                output[r][k * pat_w + j] = pattern[r][j]

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
