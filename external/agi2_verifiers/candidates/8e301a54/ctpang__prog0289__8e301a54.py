"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 8e301a54
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[289](id=289)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0289__8e301a54
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
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    components = []

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 7 and not visited[r][c]:
                color = grid[r][c]
                component = []
                stack = [(r, c)]
                visited[r][c] = True
                while stack:
                    cr, cc = stack.pop()
                    component.append((cr, cc))
                    for dr, dc in directions:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                components.append((color, component))

    # Clear all original positions
    for color, component in components:
        for r, c in component:
            output[r][c] = 7

    # Set the moved positions
    for color, component in components:
        size = len(component)
        for r, c in component:
            new_r = r + size
            if 0 <= new_r < rows:
                output[new_r][c] = color

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
