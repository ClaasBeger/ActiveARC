"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 73182012
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[244](id=244)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0244__73182012
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    rows, cols = np.where(grid != 0)
    if len(rows) == 0:
        return [[0] * 4 for _ in range(4)]
    min_r = rows.min()
    max_r = rows.max()
    min_c = cols.min()
    size = (max_r - min_r + 1) // 2
    extract_start_r = max_r - size + 1
    extract = grid[extract_start_r : max_r + 1, min_c : min_c + size]
    flipped = extract[::-1, :]
    return flipped.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
