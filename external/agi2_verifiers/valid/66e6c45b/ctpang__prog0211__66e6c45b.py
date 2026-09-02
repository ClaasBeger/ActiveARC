"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 66e6c45b
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[211](id=211)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0211__66e6c45b
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    n = len(grid)
    m = len(grid[0])
    out = [[0 for _ in range(m)] for _ in range(n)]
    out[0][0] = grid[1][1]
    out[0][m-1] = grid[1][2]
    out[n-1][0] = grid[2][1]
    out[n-1][m-1] = grid[2][2]
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
