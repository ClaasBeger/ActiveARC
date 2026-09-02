"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9b4c17c4
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[327](id=327)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0327__9b4c17c4
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
    components = []
    for i in range(rows):
        for j in range(cols):
            if grid[i, j] == 2 and not visited[i, j]:
                component = []
                stack = [(i, j)]
                visited[i, j] = True
                while stack:
                    x, y = stack.pop()
                    component.append((x, y))
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < rows and 0 <= ny < cols and grid[nx, ny] == 2 and not visited[nx, ny]:
                            visited[nx, ny] = True
                            stack.append((nx, ny))
                components.append(component)

    cols_with_8 = [j for i in range(rows) for j in range(cols) if grid[i, j] == 8]
    min_col_8 = min(cols_with_8) if cols_with_8 else 0

    cols_with_1 = [j for i in range(rows) for j in range(cols) if grid[i, j] == 1]
    max_col_1 = max(cols_with_1) if cols_with_1 else cols - 1

    output = grid.copy()
    for comp in components:
        neighbors = set()
        for x, y in comp:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols and grid[nx, ny] != 2:
                    neighbors.add(grid[nx, ny])
        if not neighbors:
            continue
        C = next(iter(neighbors))  # Assume consistent
        if C not in (1, 8):
            continue
        min_c = min(y for x, y in comp)
        max_c = max(y for x, y in comp)
        if C == 1:
            delta = max_col_1 - max_c
        else:
            delta = min_col_8 - min_c
        # Set old positions to C
        for x, y in comp:
            output[x, y] = C
        # Set new positions to 2
        for x, y in comp:
            new_y = y + delta
            if 0 <= new_y < cols:
                output[x, new_y] = 2
    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
