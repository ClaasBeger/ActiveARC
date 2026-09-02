"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ad7e01d0
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[367](id=367)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0367__ad7e01d0
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    n = len(grid)
    out = [[0 for _ in range(n * n)] for _ in range(n * n)]
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 5:
                for di in range(n):
                    for dj in range(n):
                        out[i * n + di][j * n + dj] = grid[di][dj]
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
