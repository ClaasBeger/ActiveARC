"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 8ee62060
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[292](id=292)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0292__8ee62060
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid

    height = len(grid)
    width = len(grid[0])
    visited = [[False] * width for _ in range(height)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    components = []

    def dfs(r, c):
        stack = [(r, c)]
        comp = []
        visited[r][c] = True
        while stack:
            cr, cc = stack.pop()
            comp.append((cr, cc, grid[cr][cc]))
            for dr, dc in directions:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < height and 0 <= nc < width and not visited[nr][nc] and grid[nr][nc] != 0:
                    visited[nr][nc] = True
                    stack.append((nr, nc))
        return comp

    for r in range(height):
        for c in range(width):
            if grid[r][c] != 0 and not visited[r][c]:
                comp = dfs(r, c)
                components.append(comp)

    shape_positions = []
    for comp in components:
        min_r = min(rr for rr, cc, col in comp)
        min_c = min(cc for rr, cc, col in comp)
        rel = [(rr - min_r, cc - min_c, col) for rr, cc, col in comp]
        shape_positions.append((min_r, min_c, rel))

    shape_positions.sort(key=lambda x: x[0])

    min_cs = [min_c for min_r, min_c, rel in shape_positions]
    min_cs_rev = min_cs[::-1]

    new_grid = [[0] * width for _ in range(height)]

    for i, (min_r, _, rel) in enumerate(shape_positions):
        new_min_c = min_cs_rev[i]
        for dr, dc, col in rel:
            new_r = min_r + dr
            new_c = new_min_c + dc
            new_grid[new_r][new_c] = col

    return new_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
