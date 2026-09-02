"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 33b52de3
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[101](id=101)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0101__33b52de3
"""
from __future__ import annotations



import numpy as np

import copy

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    grid = copy.deepcopy(grid)
    rows = len(grid)
    cols = len(grid[0])

    # Find key cells: color != 0 and != 5
    key_cells = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and grid[r][c] != 5:
                key_cells.append((r, c))

    if not key_cells:
        return grid

    # Find bounding box
    min_r = min(r for r, c in key_cells)
    max_r = max(r for r, c in key_cells)
    min_c = min(c for r, c in key_cells)
    max_c = max(c for r, c in key_cells)

    K = max_r - min_r + 1
    M = max_c - min_c + 1

    # Extract key
    key = [[0] * M for _ in range(K)]
    for r, c in key_cells:
        key[r - min_r][c - min_c] = grid[r][c]

    # Find connected components of 5
    visited = [[False] * cols for _ in range(rows)]
    components = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 5 and not visited[r][c]:
                comp = []
                stack = [(r, c)]
                visited[r][c] = True
                while stack:
                    cr, cc = stack.pop()
                    comp.append((cr, cc))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 5 and not visited[nr][nc]:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                components.append(comp)

    # Create block info: (min_r, min_c, comp)
    block_info = []
    for comp in components:
        if comp:
            b_min_r = min(rr for rr, cc in comp)
            b_min_c = min(cc for rr, cc in comp)
            block_info.append((b_min_r, b_min_c, comp))

    # Sort by min_r asc, then min_c asc
    block_info.sort(key=lambda x: (x[0], x[1]))

    # Assign colors
    for i in range(K):
        for j in range(M):
            idx = i * M + j
            if idx >= len(block_info):
                continue  # Safety, though should match
            _, _, positions = block_info[idx]
            color = key[i][j]
            for rr, cc in positions:
                grid[rr][cc] = color

    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
