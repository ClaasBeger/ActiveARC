"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ad38a9d0
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[366](id=366)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0366__ad38a9d0
"""
from __future__ import annotations



import numpy as np

from collections import deque

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = [row[:] for row in grid]
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    visited = set()
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def is_straight(component):
        if not component:
            return False
        rs = [r for r, c in component]
        cs = [c for r, c in component]
        return len(set(rs)) == 1 or len(set(cs)) == 1

    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 6 and (i, j) not in visited:
                component = []
                queue = deque([(i, j)])
                visited.add((i, j))
                while queue:
                    r, c = queue.popleft()
                    component.append((r, c))
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 6 and (nr, nc) not in visited:
                            visited.add((nr, nc))
                            queue.append((nr, nc))
                size = len(component)
                straight = is_straight(component)
                if size == 2:
                    color = 9
                elif size == 3:
                    color = 2 if straight else 4
                elif size == 4:
                    color = 8
                elif size == 5:
                    color = 3
                elif size == 6:
                    color = 5
                else:
                    color = 6  # fallback, though not needed
                for r, c in component:
                    grid[r][c] = color
    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
