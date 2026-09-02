"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 3b4c2228
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[116](id=116)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0116__3b4c2228
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    h = len(grid)
    w = len(grid[0])
    count = 0
    for r in range(h - 1):
        for c in range(w - 1):
            if grid[r][c] == 3 and grid[r][c + 1] == 3 and grid[r + 1][c] == 3 and grid[r + 1][c + 1] == 3:
                count += 1
    out = [[0 for _ in range(3)] for _ in range(3)]
    diag = [(0, 0), (1, 1), (2, 2)]
    for i in range(min(count, 3)):
        rr, cc = diag[i]
        out[rr][cc] = 1
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
