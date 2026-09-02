"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e9ac8c9e
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[502](id=502)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0502__e9ac8c9e
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    grid = np.array(grid)
    rows, cols = grid.shape
    visited = np.zeros((rows, cols), bool)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    def dfs(r, c):
        stack = [(r, c)]
        component = []
        while stack:
            cr, cc = stack.pop()
            if visited[cr, cc]:
                continue
            visited[cr, cc] = True
            component.append((cr, cc))
            for dr, dc in directions:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr, nc] and grid[nr, nc] == 5:
                    stack.append((nr, nc))
        return component
    
    gray_components = []
    for r in range(rows):
        for c in range(cols):
            if grid[r, c] == 5 and not visited[r, c]:
                comp = dfs(r, c)
                gray_components.append(comp)
    
    output = grid.copy()
    for comp in gray_components:
        rs = [pos[0] for pos in comp]
        cs = [pos[1] for pos in comp]
        min_r, max_r = min(rs), max(rs)
        min_c, max_c = min(cs), max(cs)
        n = max_r - min_r + 1
        h = n // 2
        mid_r = min_r + h
        mid_c = min_c + h
        
        tl = grid[min_r - 1, min_c - 1]
        tr = grid[min_r - 1, max_c + 1]
        bl = grid[max_r + 1, min_c - 1]
        br = grid[max_r + 1, max_c + 1]
        
        output[min_r - 1, min_c - 1] = 0
        output[min_r - 1, max_c + 1] = 0
        output[max_r + 1, min_c - 1] = 0
        output[max_r + 1, max_c + 1] = 0
        
        for r in range(min_r, mid_r):
            for c in range(min_c, mid_c):
                output[r, c] = tl
            for c in range(mid_c, max_c + 1):
                output[r, c] = tr
        
        for r in range(mid_r, max_r + 1):
            for c in range(min_c, mid_c):
                output[r, c] = bl
            for c in range(mid_c, max_c + 1):
                output[r, c] = br
    
    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
