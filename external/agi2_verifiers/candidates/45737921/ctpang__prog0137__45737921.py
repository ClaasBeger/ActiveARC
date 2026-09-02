"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 45737921
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[137](id=137)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0137__45737921
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def dfs(r, c, component):
        stack = [(r, c)]
        visited[r][c] = True
        component.append((r, c))
        while stack:
            cr, cc = stack.pop()
            for dr, dc in directions:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] != 0:
                    visited[nr][nc] = True
                    component.append((nr, nc))
                    stack.append((nr, nc))

    output = [row[:] for row in grid]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                component = []
                dfs(r, c, component)
                colors = set()
                for pr, pc in component:
                    colors.add(grid[pr][pc])
                if len(colors) == 2:
                    a, b = list(colors)
                    for pr, pc in component:
                        if output[pr][pc] == a:
                            output[pr][pc] = b
                        else:
                            output[pr][pc] = a
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
