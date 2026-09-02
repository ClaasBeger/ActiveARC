"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: d47aa2ff
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[446](id=446)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0446__d47aa2ff
"""
from __future__ import annotations



import numpy as np

from collections import defaultdict

def transform(grid: list[list[int]]) -> list[list[int]]:
    left = [row[0:10] for row in grid]
    right = [row[11:21] for row in grid]
    rows = len(grid)
    cols = 10
    left_pos = defaultdict(set)
    right_pos = defaultdict(set)
    for i in range(rows):
        for j in range(cols):
            c = left[i][j]
            if c != 0:
                left_pos[c].add((i, j))
            c = right[i][j]
            if c != 0:
                right_pos[c].add((i, j))
    output = [[0] * cols for _ in range(rows)]
    all_colors = set(left_pos.keys()) | set(right_pos.keys())
    for color in all_colors:
        inter = left_pos[color] & right_pos[color]
        for pos in inter:
            ii, jj = pos
            output[ii][jj] = color
        l_only = left_pos[color] - inter
        r_only = right_pos[color] - inter
        if l_only and r_only:
            l_pos = list(l_only)[0]
            r_pos = list(r_only)[0]
            output[l_pos[0]][l_pos[1]] = 2
            output[r_pos[0]][r_pos[1]] = 1
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
