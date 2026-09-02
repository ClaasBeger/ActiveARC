"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 5b6cbef5
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[192](id=192)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0192__5b6cbef5
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    small = np.array(grid)
    n = small.shape[0]  # Assuming square grid, n=4
    large_size = n * n  # 16
    large = np.zeros((large_size, large_size), dtype=int)
    for i in range(n):
        for j in range(n):
            if small[i, j] != 0:
                large[i*n : (i+1)*n, j*n : (j+1)*n] = small
    return large.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
