"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e99362f0
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[501](id=501)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0501__e99362f0
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    out = [[0 for _ in range(4)] for _ in range(5)]
    for i in range(5):
        for j in range(4):
            val_tl = grid[i][j]
            val_tr = grid[i][5 + j]
            val_bl = grid[6 + i][j]
            val_br = grid[6 + i][5 + j]
            if val_br != 0:
                out[i][j] = val_br
            elif val_tl != 0:
                out[i][j] = val_tl
            elif val_tr != 0:
                out[i][j] = val_tr
            elif val_bl != 0:
                out[i][j] = val_bl
            else:
                out[i][j] = 0
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
