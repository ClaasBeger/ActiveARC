"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e0fb7511
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[471](id=471)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0471__e0fb7511
"""
from __future__ import annotations



import numpy as np

import copy

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    
    rows = len(grid)
    cols = len(grid[0])
    output = copy.deepcopy(grid)
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    
    def dfs(r, c, component):
        stack = [(r, c)]
        visited[r][c] = True
        component.append((r, c))
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        
        while stack:
            cr, cc = stack.pop()
            for dr, dc in directions:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == 0:
                    visited[nr][nc] = True
                    component.append((nr, nc))
                    stack.append((nr, nc))
    
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 0 and not visited[i][j]:
                component = []
                dfs(i, j, component)
                if len(component) >= 2:
                    for r, c in component:
                        output[r][c] = 8
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
