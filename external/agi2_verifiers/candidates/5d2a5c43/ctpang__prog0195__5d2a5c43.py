"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 5d2a5c43
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[195](id=195)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0195__5d2a5c43
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    height = len(grid)
    width = len(grid[0])
    output = [[0 for _ in range(4)] for _ in range(height)]
    for r in range(height):
        for c in range(4):
            if grid[r][c] == 4 or (c + 5 < width and grid[r][c + 5] == 4):
                output[r][c] = 8
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
