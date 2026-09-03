"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 1a2e2828
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[41](id=41)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0041__1a2e2828
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid_lst: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid_lst)
    rows, cols = grid.shape
    candidates = set()
    # Check rows
    for i in range(rows):
        val = grid[i, 0]
        if val != 0 and np.all(grid[i, :] == val):
            candidates.add(val)
    # Check columns
    for j in range(cols):
        val = grid[0, j]
        if val != 0 and np.all(grid[:, j] == val):
            candidates.add(val)
    # Assuming exactly one candidate as per examples
    assert len(candidates) == 1
    c = next(iter(candidates))
    return [[c]]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
