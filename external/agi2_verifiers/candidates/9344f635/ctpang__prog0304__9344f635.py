"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9344f635
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[304](id=304)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0304__9344f635
"""
from __future__ import annotations



import numpy as np

from collections import deque

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def bfs(start_r, start_c):
        color = grid[start_r][start_c]
        if color == 7:
            return []
        component = []
        queue = deque([(start_r, start_c)])
        visited[start_r][start_c] = True
        while queue:
            r, c = queue.popleft()
            component.append((r, c))
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == color:
                    visited[nr][nc] = True
                    queue.append((nr, nc))
        return component

    verticals = []
    horizontals = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 7 and not visited[r][c]:
                comp = bfs(r, c)
                if len(comp) < 2:
                    continue
                rs = [pr for pr, _ in comp]
                cs = [pc for _, pc in comp]
                uniq_rs = set(rs)
                uniq_cs = set(cs)
                color = grid[rs[0]][cs[0]]
                if len(uniq_rs) == 1:  # horizontal
                    row = rs[0]
                    sorted_cs = sorted(uniq_cs)
                    if sorted_cs[-1] - sorted_cs[0] + 1 == len(sorted_cs):
                        horizontals.append((row, color))
                elif len(uniq_cs) == 1:  # vertical
                    col = cs[0]
                    sorted_rs = sorted(uniq_rs)
                    if sorted_rs[-1] - sorted_rs[0] + 1 == len(sorted_rs):
                        verticals.append((col, color))

    output = [[7 for _ in range(cols)] for _ in range(rows)]
    for col, color in verticals:
        for r in range(rows):
            output[r][col] = color
    for row, color in horizontals:
        for c in range(cols):
            output[row][c] = color
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
