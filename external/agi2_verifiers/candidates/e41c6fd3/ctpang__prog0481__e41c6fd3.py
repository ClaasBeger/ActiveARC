"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e41c6fd3
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[481](id=481)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0481__e41c6fd3
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    grid = np.array(grid)
    rows, cols = grid.shape
    visited = np.zeros((rows, cols), dtype=bool)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def dfs(r, c, color):
        component = []
        stack = [(r, c)]
        visited[r, c] = True
        while stack:
            cr, cc = stack.pop()
            component.append((cr, cc))
            for dr, dc in directions:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr, nc] and grid[nr, nc] == color:
                    visited[nr, nc] = True
                    stack.append((nr, nc))
        return component

    components = []
    for i in range(rows):
        for j in range(cols):
            if grid[i, j] != 0 and not visited[i, j]:
                color = grid[i, j]
                comp = dfs(i, j, color)
                components.append((color, comp))

    # Find purple component
    purple_comp = None
    for color, comp in components:
        if color == 8:
            purple_comp = comp
            break

    if purple_comp is None:
        return grid.tolist()

    min_row_p = min(r for r, c in purple_comp)

    output = grid.copy()

    for color, comp in components:
        if color == 8:
            continue
        min_row_s = min(r for r, c in comp)
        delta = min_row_p - min_row_s
        # Clear old positions
        for r, c in comp:
            output[r, c] = 0
        # Set new positions
        for r, c in comp:
            nr = r + delta
            if 0 <= nr < rows:
                output[nr, c] = color

    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
