"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 7953d61e
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[253](id=253)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0253__7953d61e
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    n = len(grid)
    out = [[0 for _ in range(2 * n)] for _ in range(2 * n)]

    # Top-left: copy grid
    for i in range(n):
        for j in range(n):
            out[i][j] = grid[i][j]

    # Bottom-left: 180 rotation
    for i in range(n):
        for j in range(n):
            out[n + i][j] = grid[n - 1 - i][n - 1 - j]

    # Compute transpose
    trans = [[0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            trans[i][j] = grid[j][i]

    # Top-right: vertical flip of transpose
    for i in range(n):
        for j in range(n):
            out[i][n + j] = trans[n - 1 - i][j]

    # Bottom-right: horizontal flip of transpose
    for i in range(n):
        for j in range(n):
            out[n + i][n + j] = trans[i][n - 1 - j]

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
