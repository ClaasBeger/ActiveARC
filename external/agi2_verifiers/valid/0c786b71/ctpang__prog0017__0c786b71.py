"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 0c786b71
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[17](id=17)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0017__0c786b71
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    row0 = grid[0]
    row1 = grid[1]
    row2 = grid[2]

    def construct(r):
        rev = r[::-1]
        return rev + r

    line0 = construct(row2)  # for output rows 0 and 5
    line1 = construct(row1)  # for output rows 1 and 4
    line2 = construct(row0)  # for output rows 2 and 3

    output = [
        line0,
        line1,
        line2,
        line2,
        line1,
        line0
    ]
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
