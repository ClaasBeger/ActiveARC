"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: f3cdc58f
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[521](id=521)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0521__f3cdc58f
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for r in range(rows):
        for c in range(cols):
            color = grid[r][c]
            if color in counts:
                counts[color] += 1
    output = [[0] * cols for _ in range(rows)]
    for color in range(1, 5):
        height = counts[color]
        if height > 0:
            start_row = rows - height
            col = color - 1
            for r in range(start_row, rows):
                output[r][col] = color
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
