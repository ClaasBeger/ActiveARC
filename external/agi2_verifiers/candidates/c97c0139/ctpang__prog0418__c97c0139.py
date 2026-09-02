"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: c97c0139
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[418](id=418)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0418__c97c0139
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    rows, cols = grid.shape
    output = grid.copy()
    visited = np.zeros((rows, cols), dtype=bool)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def dfs(r, c):
        component = []
        stack = [(r, c)]
        visited[r, c] = True
        while stack:
            cr, cc = stack.pop()
            component.append((cr, cc))
            for dr, dc in directions:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr, nc] and grid[nr, nc] == 2:
                    visited[nr, nc] = True
                    stack.append((nr, nc))
        return component

    for i in range(rows):
        for j in range(cols):
            if grid[i, j] == 2 and not visited[i, j]:
                comp = dfs(i, j)
                if not comp:
                    continue
                rs = [p[0] for p in comp]
                cs = [p[1] for p in comp]
                unique_rs = set(rs)
                unique_cs = set(cs)
                if len(unique_rs) == 1:  # horizontal
                    row_c = rs[0]
                    min_c = min(cs)
                    max_c = max(cs)
                    L = len(comp)
                    if max_c - min_c + 1 != L:
                        continue
                    for rr in range(rows):
                        d = abs(rr - row_c)
                        start_c = min_c + d
                        end_c = max_c - d
                        if start_c <= end_c:
                            for cc in range(start_c, end_c + 1):
                                if output[rr, cc] == 0:
                                    output[rr, cc] = 8
                elif len(unique_cs) == 1:  # vertical
                    col_c = cs[0]
                    min_r = min(rs)
                    max_r = max(rs)
                    L = len(comp)
                    if max_r - min_r + 1 != L:
                        continue
                    for cc in range(cols):
                        d = abs(cc - col_c)
                        start_r = min_r + d
                        end_r = max_r - d
                        if start_r <= end_r:
                            for rr in range(start_r, end_r + 1):
                                if output[rr, cc] == 0:
                                    output[rr, cc] = 8
    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
