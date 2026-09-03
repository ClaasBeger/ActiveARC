"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 2753e76c
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[78](id=78)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0078__2753e76c
"""
from __future__ import annotations



import numpy as np

from collections import defaultdict

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    count = defaultdict(int)
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != 0 and not visited[i][j]:
                color = grid[i][j]
                stack = [(i, j)]
                visited[i][j] = True
                while stack:
                    r, c = stack.pop()
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                count[color] += 1
    items = [(cnt, colr) for colr, cnt in count.items() if cnt > 0]
    if not items:
        return []
    items.sort(key=lambda x: (-x[0], x[1]))
    num_rows = len(items)
    max_col = max(cnt for cnt, _ in items)
    output = [[0] * max_col for _ in range(num_rows)]
    for i, (cnt, colr) in enumerate(items):
        start = max_col - cnt
        for j in range(cnt):
            output[i][start + j] = colr
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
