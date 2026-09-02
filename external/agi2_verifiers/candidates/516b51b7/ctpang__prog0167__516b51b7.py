"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 516b51b7
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[167](id=167)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0167__516b51b7
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

    def fill_rect(minr, maxr, minc, maxc, color):
        h = maxr - minr + 1
        w = maxc - minc + 1
        if h < 3 or w < 3:
            return
        for r in range(minr + 1, maxr):
            for c in range(minc + 1, maxc):
                grid[r][c] = color
        next_color = 5 - color
        fill_rect(minr + 1, maxr - 1, minc + 1, maxc - 1, next_color)

    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 1 and not visited[i][j]:
                minr = maxr = i
                minc = maxc = j
                q = deque([(i, j)])
                visited[i][j] = True
                while q:
                    r, c = q.popleft()
                    minr = min(minr, r)
                    maxr = max(maxr, r)
                    minc = min(minc, c)
                    maxc = max(maxc, c)
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1 and not visited[nr][nc]:
                            visited[nr][nc] = True
                            q.append((nr, nc))
                fill_rect(minr, maxr, minc, maxc, 2)
    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
