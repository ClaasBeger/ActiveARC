"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 68b67ca3
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[222](id=222)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0222__68b67ca3
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    output = []
    for r in range(3):
        row = []
        for c in range(3):
            row.append(grid[2 * r][2 * c])
        output.append(row)
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
