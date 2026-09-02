"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 319f2597
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[93](id=93)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0093__319f2597
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    rows_with_zero = set()
    cols_with_zero = set()
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                rows_with_zero.add(r)
                cols_with_zero.add(c)
    output = [row[:] for row in grid]
    for r in range(rows):
        for c in range(cols):
            if r in rows_with_zero or c in cols_with_zero:
                output[r][c] = grid[r][c] if grid[r][c] == 2 else 0
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
