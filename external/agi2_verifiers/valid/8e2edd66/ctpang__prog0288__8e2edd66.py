"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 8e2edd66
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[288](id=288)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0288__8e2edd66
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    input_grid = np.array(grid)
    C = np.max(input_grid)  # The non-zero color
    output = np.zeros((9, 9), dtype=int)
    for r in range(9):
        d1 = r // 3
        d0 = r % 3
        for c in range(9):
            e1 = c // 3
            e0 = c % 3
            if input_grid[d1, e1] == 0 and input_grid[d0, e0] == 0:
                output[r, c] = C
    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
