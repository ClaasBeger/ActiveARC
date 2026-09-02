"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e57337a4
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[486](id=486)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0486__e57337a4
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid:
        return []
    h = len(grid)
    w = len(grid[0])
    # Find background color (first non-0)
    background = None
    for row in grid:
        for cell in row:
            if cell != 0:
                background = cell
                break
        if background is not None:
            break
    # Assume square grid, k=3
    k = 3
    super_size = h // k
    # Initialize output
    output = [[background for _ in range(k)] for _ in range(k)]
    # Set 0 in super positions where input has 0
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 0:
                sr = r // super_size
                sc = c // super_size
                output[sr][sc] = 0
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
