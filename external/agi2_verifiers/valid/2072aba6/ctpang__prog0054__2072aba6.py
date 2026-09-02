"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 2072aba6
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[54](id=54)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0054__2072aba6
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    g = np.array(grid)
    out = np.zeros((6, 6), dtype=int)
    for i in range(3):
        for j in range(3):
            if g[i, j] == 5:
                out[2*i:2*i+2, 2*j:2*j+2] = [[1, 2], [2, 1]]
    return out.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
