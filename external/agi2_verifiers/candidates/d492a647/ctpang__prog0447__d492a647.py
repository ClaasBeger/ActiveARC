"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: d492a647
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[447](id=447)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0447__d492a647
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    rows = len(grid)
    cols = len(grid[0])
    # Find the special cell
    special_r = special_c = special_color = None
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != 0 and grid[i][j] != 5:
                special_r = i
                special_c = j
                special_color = grid[i][j]
                break  # Assume only one
        if special_r is not None:
            break
    if special_color is None:
        return [row[:] for row in grid]
    parity_row = special_r % 2
    parity_col = special_c % 2
    output = [row[:] for row in grid]
    for i in range(rows):
        if i % 2 == parity_row:
            for j in range(cols):
                if j % 2 == parity_col and output[i][j] == 0:
                    output[i][j] = special_color
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
