"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 7e4d4f7c
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[260](id=260)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0260__7e4d4f7c
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if len(grid) < 3:
        return grid  # Though not needed for given inputs, as safeguard
    first_row = grid[0][:]
    second_row = grid[1][:]
    B = grid[2][0]  # Background color, assuming row 2 is uniform
    third_row = [x if x == B else 6 for x in first_row]
    return [first_row, second_row, third_row]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
