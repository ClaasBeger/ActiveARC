"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 60c09cac
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[199](id=199)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0199__60c09cac
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    g = np.array(grid)
    rows, cols = g.shape
    out = np.zeros((2 * rows, 2 * cols), dtype=int)
    for r in range(rows):
        for c in range(cols):
            if g[r, c] != 0:
                out[2 * r:2 * r + 2, 2 * c:2 * c + 2] = g[r, c]
    return out.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
