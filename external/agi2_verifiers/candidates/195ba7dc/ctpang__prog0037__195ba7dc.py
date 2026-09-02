"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 195ba7dc
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[37](id=37)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0037__195ba7dc
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    out = []
    for r in range(5):
        left = [1 if grid[r][c] == 7 else 0 for c in range(6)]
        right = [1 if grid[r][c] == 7 else 0 for c in range(7, 13)]
        row = [1 if left[c] or right[c] else 0 for c in range(6)]
        out.append(row)
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
