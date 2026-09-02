"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: c658a4bd
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[412](id=412)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0412__c658a4bd
"""
from __future__ import annotations



import numpy as np

from collections import defaultdict

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    h = len(grid)
    w = len(grid[0])
    pos = defaultdict(list)
    for i in range(h):
        for j in range(w):
            c = grid[i][j]
            if c != 0:
                pos[c].append((i, j))
    components = []
    for c, lst in pos.items():
        if not lst:
            continue
        min_i = min(p[0] for p in lst)
        max_i = max(p[0] for p in lst)
        min_j = min(p[1] for p in lst)
        max_j = max(p[1] for p in lst)
        bh = max_i - min_i + 1
        bw = max_j - min_j + 1
        bs = max(bh, bw)
        components.append((bs, c))
    if not components:
        return [[0]]
    components.sort(reverse=True)
    n = components[0][0]
    out = [[0] * n for _ in range(n)]
    for s, c in components:
        offset = (n - s) // 2
        sr = offset
        er = sr + s - 1
        sc = offset
        ec = sc + s - 1
        # top
        for j in range(sc, ec + 1):
            out[sr][j] = c
        # bottom
        for j in range(sc, ec + 1):
            out[er][j] = c
        # left
        for i in range(sr + 1, er):
            out[i][sc] = c
        # right
        for i in range(sr + 1, er):
            out[i][ec] = c
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
