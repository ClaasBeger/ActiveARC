"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: a57f2f04
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[344](id=344)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0344__a57f2f04
"""
from __future__ import annotations



import numpy as np

import copy

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = copy.deepcopy(grid)
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def dfs(r, c, component):
        stack = [(r, c)]
        visited[r][c] = True
        component.append((r, c))
        while stack:
            cr, cc = stack.pop()
            for dr, dc in directions:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] != 8:
                    visited[nr][nc] = True
                    stack.append((nr, nc))
                    component.append((nr, nc))

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 8 and not visited[r][c]:
                component = []
                dfs(r, c, component)
                if not component:
                    continue
                big_min_r = min(rr for rr, cc in component)
                big_max_r = max(rr for rr, cc in component)
                big_min_c = min(cc for rr, cc in component)
                big_max_c = max(cc for rr, cc in component)
                big_h = big_max_r - big_min_r + 1
                big_w = big_max_c - big_min_c + 1
                colored = [(rr, cc) for rr, cc in component if grid[rr][cc] != 0]
                if not colored:
                    continue
                pat_min_r = min(rr for rr, cc in colored)
                pat_max_r = max(rr for rr, cc in colored)
                pat_min_c = min(cc for rr, cc in colored)
                pat_max_c = max(cc for rr, cc in colored)
                pat_h = pat_max_r - pat_min_r + 1
                pat_w = pat_max_c - pat_min_c + 1
                pattern = [[grid[pat_min_r + i][pat_min_c + j] for j in range(pat_w)] for i in range(pat_h)]
                for i in range(big_h):
                    for j in range(big_w):
                        rr = big_min_r + i
                        cc = big_min_c + j
                        grid[rr][cc] = pattern[i % pat_h][j % pat_w]
    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
