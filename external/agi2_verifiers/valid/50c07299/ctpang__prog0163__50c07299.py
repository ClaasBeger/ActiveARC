"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 50c07299
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[163](id=163)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0163__50c07299
"""
from __future__ import annotations



import numpy as np

import copy

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = copy.deepcopy(grid)
    rows = len(grid)
    diag = rows - 1

    # Find current red positions on the diagonal
    reds = [(r, c) for r in range(rows) for c in range(rows) if grid[r][c] == 2 and r + c == diag]
    if not reds:
        return grid

    # Sort by row
    reds.sort()
    s = reds[0][0]
    l = len(reds)

    # Set old reds to 7
    for r, c in reds:
        grid[r][c] = 7

    # Compute new start and length
    new_l = l + 1
    new_s = s - new_l

    # Place new reds
    for i in range(new_l):
        r = new_s + i
        c = diag - r
        if 0 <= r < rows and 0 <= c < rows:
            grid[r][c] = 2

    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
