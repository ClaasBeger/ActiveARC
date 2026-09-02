"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: da2b0fe3
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[460](id=460)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0460__da2b0fe3
"""
from __future__ import annotations



import numpy as np

import copy

def transform(grid: list[list[int]]) -> list[list[int]]:
    output = copy.deepcopy(grid)
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    visited = set()
    components = []

    def dfs(r, c, comp):
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if (cr, cc) in visited:
                continue
            visited.add((cr, cc))
            comp.append((cr, cc))
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr = cr + dr
                nc = cc + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 0 and (nr, nc) not in visited:
                    stack.append((nr, nc))

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and (r, c) not in visited:
                comp = []
                dfs(r, c, comp)
                components.append(comp)

    if len(components) != 2:
        return output  # Assume exactly two, but return unchanged if not

    bbs = []
    for comp in components:
        rs = [p[0] for p in comp]
        cs = [p[1] for p in comp]
        min_r = min(rs)
        max_r = max(rs)
        min_c = min(cs)
        max_c = max(cs)
        bbs.append((min_r, max_r, min_c, max_c))

    bb1, bb2 = bbs
    min_r1, max_r1, min_c1, max_c1 = bb1
    min_r2, max_r2, min_c2, max_c2 = bb2

    row_overlap = max(min_r1, min_r2) <= min(max_r1, max_r2)
    col_overlap = max(min_c1, min_c2) <= min(max_c1, max_c2)

    if row_overlap and not col_overlap:
        # Horizontal separation
        if min_c1 < min_c2:
            left_max_c = max_c1
            right_min_c = min_c2
        else:
            left_max_c = max_c2
            right_min_c = min_c1
        start_c = left_max_c + 1
        end_c = right_min_c - 1
        for c in range(start_c, end_c + 1):
            for r in range(rows):
                output[r][c] = 3
    elif col_overlap and not row_overlap:
        # Vertical separation
        if min_r1 < min_r2:
            upper_max_r = max_r1
            lower_min_r = min_r2
        else:
            upper_max_r = max_r2
            lower_min_r = min_r1
        start_r = upper_max_r + 1
        end_r = lower_min_r - 1
        for r in range(start_r, end_r + 1):
            for c in range(cols):
                output[r][c] = 3

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
