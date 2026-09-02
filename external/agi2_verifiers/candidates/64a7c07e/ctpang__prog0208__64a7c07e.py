"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 64a7c07e
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[208](id=208)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0208__64a7c07e
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    output = [row[:] for row in grid]
    visited = [[False] * cols for _ in range(rows)]
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dfs(r, c, component):
        stack = [(r, c)]
        visited[r][c] = True
        component.append((r, c))
        while stack:
            cr, cc = stack.pop()
            for dr, dc in directions:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == 8:
                    visited[nr][nc] = True
                    stack.append((nr, nc))
                    component.append((nr, nc))

    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 8 and not visited[i][j]:
                component = []
                dfs(i, j, component)
                if component:
                    min_c = min(cc for _, cc in component)
                    max_c = max(cc for _, cc in component)
                    w = max_c - min_c + 1
                    # Clear original positions
                    for cr, cc in component:
                        output[cr][cc] = 0
                    # Set new positions
                    for cr, cc in component:
                        new_c = cc + w
                        if new_c < cols:
                            output[cr][new_c] = 8

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
