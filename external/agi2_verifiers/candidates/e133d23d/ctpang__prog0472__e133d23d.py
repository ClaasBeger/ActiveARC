"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e133d23d
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[472](id=472)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0472__e133d23d
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    output = [[2 for _ in range(3)] for _ in range(3)]
    for i in range(3):
        for j in range(3):
            if grid[i][j] == 0 and grid[i][j + 4] == 0:
                output[i][j] = 0
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
