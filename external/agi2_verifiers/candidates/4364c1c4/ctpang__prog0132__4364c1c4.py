"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 4364c1c4
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[132](id=132)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0132__4364c1c4
"""
from __future__ import annotations



import numpy as np

from collections import deque

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    bg = grid[0][0]
    visited = [[False] * cols for _ in range(rows)]
    components = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != bg and not visited[r][c]:
                color = grid[r][c]
                comp = []
                q = deque([(r, c)])
                visited[r][c] = True
                while q:
                    x, y = q.popleft()
                    comp.append((x, y))
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < rows and 0 <= ny < cols and not visited[nx][ny] and grid[nx][ny] == color:
                            visited[nx][ny] = True
                            q.append((nx, ny))
                min_r = min(rx for rx, _ in comp)
                components.append((min_r, comp, color))
    components.sort(key=lambda x: x[0])
    for i, (_, comp, color) in enumerate(components):
        shift = -1 if i % 2 == 0 else 1
        # clear
        for r, c in comp:
            grid[r][c] = bg
        # set new
        for r, c in comp:
            new_c = c + shift
            if 0 <= new_c < cols:
                grid[r][new_c] = color
    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
