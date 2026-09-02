"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ae58858e
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[370](id=370)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0370__ae58858e
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    output = [row[:] for row in grid]  # copy the grid

    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 2 and not visited[i][j]:
                component = []
                stack = [(i, j)]
                visited[i][j] = True
                component.append((i, j))
                size = 1
                while stack:
                    r, c = stack.pop()
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == 2:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                            component.append((nr, nc))
                            size += 1
                if size >= 4:
                    for pr, pc in component:
                        output[pr][pc] = 6
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
