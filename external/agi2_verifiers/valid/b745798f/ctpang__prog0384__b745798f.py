"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: b745798f
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[384](id=384)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0384__b745798f
"""
from __future__ import annotations



import numpy as np

from collections import deque

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid:
        return []
    n = len(grid)
    if n == 0:
        return []
    # Assume square
    assert all(len(row) == n for row in grid)

    # Find components
    visited = [[False] * n for _ in range(n)]
    corner_colors = {1: 8, 2: 8, 3: 8, 4: 8}  # Default to 8 if missing
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for i in range(n):
        for j in range(n):
            if grid[i][j] != 8 and not visited[i][j]:
                # Flood fill to find component
                color = grid[i][j]
                component = []
                queue = deque([(i, j)])
                visited[i][j] = True
                while queue:
                    x, y = queue.popleft()
                    component.append((x, y))
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < n and 0 <= ny < n and not visited[nx][ny] and grid[nx][ny] == color:
                            visited[nx][ny] = True
                            queue.append((nx, ny))

                # Determine orientation
                min_r = min(r for r, c in component)
                min_c = min(c for r, c in component)
                rel = sorted([(r - min_r, c - min_c) for r, c in component])
                types = {
                    tuple(sorted([(0,0),(0,1),(1,0)])): 1,
                    tuple(sorted([(0,0),(1,0),(1,1)])): 2,
                    tuple(sorted([(0,1),(1,0),(1,1)])): 3,
                    tuple(sorted([(0,0),(0,1),(1,1)])): 4
                }
                shape_tuple = tuple(rel)
                if shape_tuple in types:
                    typ = types[shape_tuple]
                    corner_colors[typ] = color

    # Create output grid all 8
    output = [[8] * n for _ in range(n)]

    # k = (n - 1) // 2
    k = (n - 1) // 2

    # Top-left: type 1
    color = corner_colors[1]
    # Top row, left k cells
    for c in range(k):
        output[0][c] = color
    # Left column, rows 1 to k-1
    for r in range(1, k):
        output[r][0] = color

    # Top-right: type 4
    color = corner_colors[4]
    # Top row, right k cells
    for c in range(n - k, n):
        output[0][c] = color
    # Right column, rows 1 to k-1
    for r in range(1, k):
        output[r][n - 1] = color

    # Bottom-left: type 2
    color = corner_colors[2]
    # Bottom row, left k cells
    for c in range(k):
        output[n - 1][c] = color
    # Left column, rows n-k to n-2
    for r in range(n - k, n - 1):
        output[r][0] = color

    # Bottom-right: type 3
    color = corner_colors[3]
    # Bottom row, right k cells
    for c in range(n - k, n):
        output[n - 1][c] = color
    # Right column, rows n-k to n-2
    for r in range(n - k, n - 1):
        output[r][n - 1] = color

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
