"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 17b80ad2
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[35](id=35)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0035__17b80ad2
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    output = [row[:] for row in grid]
    rows = len(grid)
    cols = len(grid[0])
    bottom_row = rows - 1
    for c in range(cols):
        if grid[bottom_row][c] == 5:
            # Collect colored positions
            colored = []
            for r in range(rows):
                if grid[r][c] != 0:
                    colored.append((r, grid[r][c]))
            if not colored:
                continue
            # Fill segments
            prev_r = -1
            for r, color in colored:
                start = prev_r + 1
                end = r
                for rr in range(start, end + 1):
                    output[rr][c] = color
                prev_r = r
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
