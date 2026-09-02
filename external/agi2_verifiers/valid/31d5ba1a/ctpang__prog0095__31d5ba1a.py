"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 31d5ba1a
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[95](id=95)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0095__31d5ba1a
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    h = len(grid) // 2
    w = len(grid[0]) if grid else 0
    output = [[0 for _ in range(w)] for _ in range(h)]
    for r in range(h):
        for c in range(w):
            top = grid[r][c] != 0
            bottom = grid[r + h][c] != 0
            if top + bottom == 1:
                output[r][c] = 6
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
