"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: be03b35f
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[403](id=403)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0403__be03b35f
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    # Extract top-right 2x2 subgrid (rows 0-1, columns 3-4)
    subgrid = [row[3:5] for row in grid[0:2]]
    # Rotate 180 degrees: reverse rows, then reverse each row
    rotated = [row[::-1] for row in subgrid[::-1]]
    return rotated

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
