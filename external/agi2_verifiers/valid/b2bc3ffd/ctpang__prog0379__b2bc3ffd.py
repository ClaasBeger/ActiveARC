"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: b2bc3ffd
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[379](id=379)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0379__b2bc3ffd
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    rows, cols = grid.shape
    output = grid.copy()
    visited = np.zeros_like(grid, dtype=bool)
    
    for i in range(rows):
        for j in range(cols):
            color = grid[i, j]
            if not visited[i, j] and color != 0 and color != 7 and color != 8:
                component = []
                stack = [(i, j)]
                visited[i, j] = True
                while stack:
                    x, y = stack.pop()
                    component.append((x, y))
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < rows and 0 <= ny < cols and not visited[nx, ny] and grid[nx, ny] == color:
                            visited[nx, ny] = True
                            stack.append((nx, ny))
                size = len(component)
                # Clear original positions
                for x, y in component:
                    output[x, y] = 7
                # Place at new positions
                for x, y in component:
                    nx = x - size
                    output[nx, y] = color
    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
