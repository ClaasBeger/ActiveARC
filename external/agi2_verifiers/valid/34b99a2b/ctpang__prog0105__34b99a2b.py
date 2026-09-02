"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 34b99a2b
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[105](id=105)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0105__34b99a2b
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    out = [[0] * 4 for _ in range(rows)]
    for r in range(rows):
        for c in range(4):
            left = 1 if grid[r][c] == 8 else 0
            right = 1 if grid[r][c + 5] == 5 else 0
            xor = left ^ right
            out[r][c] = 2 if xor == 1 else 0
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
