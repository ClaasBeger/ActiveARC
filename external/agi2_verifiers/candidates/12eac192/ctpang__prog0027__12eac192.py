"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 12eac192
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[27](id=27)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0027__12eac192
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    height = len(grid)
    width = len(grid[0])
    output = [row[:] for row in grid]
    visited = [[False for _ in range(width)] for _ in range(height)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    def dfs(r, c, color, component):
        stack = [(r, c)]
        visited[r][c] = True
        component.append((r, c))
        
        while stack:
            cr, cc = stack.pop()
            for dr, dc in directions:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < height and 0 <= nc < width and not visited[nr][nc] and grid[nr][nc] == color:
                    visited[nr][nc] = True
                    component.append((nr, nc))
                    stack.append((nr, nc))
    
    for r in range(height):
        for c in range(width):
            if grid[r][c] != 0 and not visited[r][c]:
                component = []
                dfs(r, c, grid[r][c], component)
                if len(component) <= 2:
                    for cr, cc in component:
                        output[cr][cc] = 3
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
