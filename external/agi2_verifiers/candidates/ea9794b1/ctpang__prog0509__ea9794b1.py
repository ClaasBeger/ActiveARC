"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ea9794b1
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[509](id=509)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0509__ea9794b1
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    N = len(grid) // 2
    out = [[0 for _ in range(N)] for _ in range(N)]
    for i in range(N):
        for j in range(N):
            G = grid[i][j + N]
            P = grid[i + N][j]
            B = grid[i + N][j + N]
            Y = grid[i][j]
            if G != 0:
                out[i][j] = G
            elif P != 0:
                out[i][j] = P
            elif B != 0:
                out[i][j] = B
            elif Y != 0:
                out[i][j] = Y
            else:
                out[i][j] = 0
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
