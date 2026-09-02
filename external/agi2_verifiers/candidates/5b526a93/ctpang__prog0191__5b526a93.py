"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 5b526a93
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[191](id=191)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0191__5b526a93
"""
from __future__ import annotations



import numpy as np

from collections import defaultdict

def transform(grid: list[list[int]]) -> list[list[int]]:
    h = len(grid)
    w = len(grid[0])
    groups = defaultdict(list)  # r -> list of c
    for r in range(h - 2):
        for c in range(w - 2):
            if (grid[r][c] == 1 and grid[r][c + 1] == 1 and grid[r][c + 2] == 1 and
                grid[r + 1][c] == 1 and grid[r + 1][c + 1] == 0 and grid[r + 1][c + 2] == 1 and
                grid[r + 2][c] == 1 and grid[r + 2][c + 1] == 1 and grid[r + 2][c + 2] == 1):
                groups[r].append(c)
    if not groups:
        return grid
    max_len = max(len(cs) for cs in groups.values())
    ref_r = next(r for r in groups if len(groups[r]) == max_len)
    ref_cs = set(groups[ref_r])
    output = [row[:] for row in grid]
    for r in groups:
        if len(groups[r]) >= max_len:
            continue
        current_cs = set(groups[r])
        for c in ref_cs - current_cs:
            output[r][c] = 8
            output[r][c + 1] = 8
            output[r][c + 2] = 8
            output[r + 1][c] = 8
            # center remains 0
            output[r + 1][c + 2] = 8
            output[r + 2][c] = 8
            output[r + 2][c + 1] = 8
            output[r + 2][c + 2] = 8
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
