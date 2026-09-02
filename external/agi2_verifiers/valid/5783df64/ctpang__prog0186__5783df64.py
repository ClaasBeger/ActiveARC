"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 5783df64
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[186](id=186)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0186__5783df64
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    g = np.array(grid)
    nonzeros = np.argwhere(g != 0)
    c = len(nonzeros)
    n = int(np.sqrt(c))
    m = g.shape[0]
    k = m // n
    out = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            block = g[i * k:(i + 1) * k, j * k:(j + 1) * k]
            colors = block[block != 0]
            out[i, j] = colors[0]
    return out.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
