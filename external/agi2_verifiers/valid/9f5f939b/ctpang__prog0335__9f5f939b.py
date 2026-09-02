"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9f5f939b
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[335](id=335)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0335__9f5f939b
"""
from __future__ import annotations



import numpy as np

import copy

def transform(grid: list[list[int]]) -> list[list[int]]:
    output = copy.deepcopy(grid)
    rows = len(grid)
    if rows == 0:
        return output
    cols = len(grid[0])

    # Find all candidate positions from vertical patterns
    candidates = set()
    for c in range(cols):
        for k in range(rows - 6):
            if (grid[k][c] == 1 and grid[k+1][c] == 1 and
                grid[k+2][c] == 8 and grid[k+3][c] == 8 and grid[k+4][c] == 8 and
                grid[k+5][c] == 1 and grid[k+6][c] == 1 and
                (k == 0 or grid[k-1][c] != 1) and
                (k+7 >= rows or grid[k+7][c] != 1)):
                r = k + 3
                candidates.add((r, c))

    # For each candidate, check horizontal pattern
    for r, c in candidates:
        m = c - 3
        if m >= 0 and m + 6 < cols:
            if (grid[r][m] == 1 and grid[r][m+1] == 1 and
                grid[r][m+2] == 8 and grid[r][m+3] == 8 and grid[r][m+4] == 8 and
                grid[r][m+5] == 1 and grid[r][m+6] == 1 and
                (m == 0 or grid[r][m-1] != 1) and
                (m+7 >= cols or grid[r][m+7] != 1)):
                output[r][c] = 4

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
