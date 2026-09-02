"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 551d5bf1
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[177](id=177)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0177__551d5bf1
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    rows, cols = grid.shape
    output = grid.copy()
    visited = np.zeros((rows, cols), bool)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def dfs(r, c, component):
        stack = [(r, c)]
        visited[r, c] = True
        component.append((r, c))
        while stack:
            cr, cc = stack.pop()
            for dr, dc in directions:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr, nc] and grid[nr, nc] == 1:
                    visited[nr, nc] = True
                    stack.append((nr, nc))
                    component.append((nr, nc))

    components = []
    for i in range(rows):
        for j in range(cols):
            if grid[i, j] == 1 and not visited[i, j]:
                comp = []
                dfs(i, j, comp)
                components.append(comp)

    for comp in components:
        if not comp:
            continue
        rs = [p[0] for p in comp]
        cs = [p[1] for p in comp]
        min_r = min(rs)
        max_r = max(rs)
        min_c = min(cs)
        max_c = max(cs)
        # Fill all 0 in the box to 8
        for ii in range(min_r, max_r + 1):
            for jj in range(min_c, max_c + 1):
                if grid[ii, jj] == 0:
                    output[ii, jj] = 8
        # Now find gaps and extend
        for ii in range(min_r, max_r + 1):
            for jj in range(min_c, max_c + 1):
                if grid[ii, jj] == 0 and (ii == min_r or ii == max_r or jj == min_c or jj == max_c):
                    # Extend based on sides
                    if jj == min_c:  # left
                        for cc in range(0, min_c):
                            output[ii, cc] = 8
                    if jj == max_c:  # right
                        for cc in range(max_c + 1, cols):
                            output[ii, cc] = 8
                    if ii == min_r:  # top
                        for rr in range(0, min_r):
                            output[rr, jj] = 8
                    if ii == max_r:  # bottom
                        for rr in range(max_r + 1, rows):
                            output[rr, jj] = 8

    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
