"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 32e9702f
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[97](id=97)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0097__32e9702f
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    output = [[5 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        c = 0
        while c < cols:
            if grid[r][c] != 0:
                color = grid[r][c]
                start = c
                while c < cols and grid[r][c] == color:
                    c += 1
                end = c - 1
                new_start = start - 1 if start > 0 else 0
                new_end = end - 1
                if new_end >= new_start:
                    for cc in range(new_start, new_end + 1):
                        output[r][cc] = color
            else:
                c += 1
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
