"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e74e1818
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[490](id=490)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0490__e74e1818
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid:
        return grid
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    color_ranges = {}
    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]
            if val != 0:
                if val not in color_ranges:
                    color_ranges[val] = [r, r]
                else:
                    color_ranges[val][0] = min(color_ranges[val][0], r)
                    color_ranges[val][1] = max(color_ranges[val][1], r)
    output = [row[:] for row in grid]
    for colr, (min_r, max_r) in color_ranges.items():
        block_rows = [grid[r][:] for r in range(min_r, max_r + 1)]
        block_rows.reverse()
        for i, r in enumerate(range(min_r, max_r + 1)):
            output[r] = block_rows[i]
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
