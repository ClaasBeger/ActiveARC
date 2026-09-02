"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e345f17b
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[479](id=479)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0479__e345f17b
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid:
        return []
    rows = len(grid)
    output = [[0 for _ in range(4)] for _ in range(rows)]
    for i in range(rows):
        for j in range(4):
            if grid[i][j] == 0 and grid[i][j + 4] == 0:
                output[i][j] = 4
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
