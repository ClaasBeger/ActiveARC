"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 25e02866
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[73](id=73)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0073__25e02866
"""
from __future__ import annotations



import numpy as np

from collections import Counter

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    
    rows = len(grid)
    cols = len(grid[0])
    background = grid[0][0]
    visited = [[False] * cols for _ in range(rows)]
    components = []
    
    def dfs(x, y, comp):
        stack = [(x, y)]
        visited[x][y] = True
        comp.append((x, y))
        while stack:
            cx, cy = stack.pop()
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < rows and 0 <= ny < cols and not visited[nx][ny] and grid[nx][ny] != background:
                    visited[nx][ny] = True
                    stack.append((nx, ny))
                    comp.append((nx, ny))
    
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != background and not visited[i][j]:
                comp = []
                dfs(i, j, comp)
                components.append(comp)
    
    squares = []
    for comp in components:
        if not comp:
            continue
        rs = [r for r, c in comp]
        cs = [c for r, c in comp]
        min_r, max_r = min(rs), max(rs)
        min_c, max_c = min(cs), max(cs)
        h = max_r - min_r + 1
        w = max_c - min_c + 1
        if h == w and len(comp) == h * w:
            squares.append((min_r, min_c, h))
    
    if not squares:
        return []
    
    n = squares[0][2]
    # Get frame_color from most common in first square
    first_min_r, first_min_c, _ = squares[0]
    colors = [grid[first_min_r + i][first_min_c + j] for i in range(n) for j in range(n)]
    frame_color = Counter(colors).most_common(1)[0][0]
    
    output = [[frame_color for _ in range(n)] for _ in range(n)]
    
    for min_r, min_c, _ in squares:
        for i in range(n):
            for j in range(n):
                color = grid[min_r + i][min_c + j]
                if color != frame_color:
                    output[i][j] = color
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
