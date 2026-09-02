"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: aaef0977
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[362](id=362)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0362__aaef0977
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    r, c, C = None, None, None
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != 7:
                r, c, C = i, j, grid[i][j]
                break
        if r is not None:
            break
    base = [5, 2, 8, 9, 6, 1, 3, 4, 0]
    k = base.index(C)
    used = base[k:] + base[:k]
    output = [[0 for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            dist = abs(i - r) + abs(j - c)
            output[i][j] = used[dist % 9]
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
