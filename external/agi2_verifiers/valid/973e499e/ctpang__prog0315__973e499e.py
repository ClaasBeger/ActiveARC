"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 973e499e
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[315](id=315)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0315__973e499e
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid_lst: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid_lst)
    n = grid.shape[0]  # assume square
    large = np.zeros((n * n, n * n), dtype=int)
    for i in range(n):
        for j in range(n):
            c = grid[i, j]
            for k in range(n):
                for l in range(n):
                    if grid[k, l] == c:
                        large[n * i + k, n * j + l] = c
    return large.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
