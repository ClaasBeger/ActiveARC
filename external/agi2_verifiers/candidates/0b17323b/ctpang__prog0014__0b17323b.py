"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 0b17323b
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[14](id=14)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0014__0b17323b
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    n = len(grid)
    ps = []
    for i in range(n):
        if grid[i][i] == 1:
            ps.append(i)
    if len(ps) < 2:
        return grid
    ps.sort()
    d = ps[1] - ps[0]
    for j in range(1, len(ps)):
        if ps[j] - ps[j - 1] != d:
            return grid  # Not arithmetic
    current = ps[-1] + d
    while current < n:
        if grid[current][current] == 0:
            grid[current][current] = 2
        current += d
    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
