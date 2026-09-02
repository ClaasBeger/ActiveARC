"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 84db8fc4
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[271](id=271)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0271__84db8fc4
"""
from __future__ import annotations



import numpy as np

import copy
from collections import deque

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    h = len(grid)
    w = len(grid[0])
    out = copy.deepcopy(grid)
    q = deque()
    # Collect all border cells that are 0
    for r in range(h):
        for c in range(w):
            if out[r][c] == 0 and (r == 0 or r == h - 1 or c == 0 or c == w - 1):
                out[r][c] = 2
                q.append((r, c))
    # Directions for 4-connectivity
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    # BFS to flood fill with 2
    while q:
        r, c = q.popleft()
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w and out[nr][nc] == 0:
                out[nr][nc] = 2
                q.append((nr, nc))
    # Fill remaining 0s with 5
    for r in range(h):
        for c in range(w):
            if out[r][c] == 0:
                out[r][c] = 5
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
