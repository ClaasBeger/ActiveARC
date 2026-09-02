"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e7639916
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[491](id=491)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0491__e7639916
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid:
        return grid
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    positions = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 8:
                positions.append((r, c))
    if not positions:
        return [row[:] for row in grid]
    rs = [p[0] for p in positions]
    cs = [p[1] for p in positions]
    min_r = min(rs)
    max_r = max(rs)
    min_c = min(cs)
    max_c = max(cs)
    output = [row[:] for row in grid]
    # Top border
    for c in range(min_c, max_c + 1):
        if output[min_r][c] == 0:
            output[min_r][c] = 1
    # Bottom border
    for c in range(min_c, max_c + 1):
        if output[max_r][c] == 0:
            output[max_r][c] = 1
    # Left border
    for r in range(min_r, max_r + 1):
        if output[r][min_c] == 0:
            output[r][min_c] = 1
    # Right border
    for r in range(min_r, max_r + 1):
        if output[r][max_c] == 0:
            output[r][max_c] = 1
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
