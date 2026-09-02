"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: a59b95c0
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[345](id=345)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0345__a59b95c0
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    small = np.array(grid)
    flat = small.flatten()
    unique = set(flat)
    k = len(unique)
    n = small.shape[0]
    large = np.zeros((n * k, n * k), dtype=int)
    for i in range(k):
        for j in range(k):
            large[i * n : (i + 1) * n, j * n : (j + 1) * n] = small
    return large.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
