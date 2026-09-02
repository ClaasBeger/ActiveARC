"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 2a5f8217
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[86](id=86)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0086__2a5f8217
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid

    height = len(grid)
    width = len(grid[0])
    output = [row[:] for row in grid]
    visited = [[False] * width for _ in range(height)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    components = []

    def dfs(r, c, color):
        stack = [(r, c)]
        component = [(r, c)]
        visited[r][c] = True
        while stack:
            cr, cc = stack.pop()
            for dr, dc in directions:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < height and 0 <= nc < width and not visited[nr][nc] and grid[nr][nc] == color:
                    visited[nr][nc] = True
                    component.append((nr, nc))
                    stack.append((nr, nc))
        return component

    for r in range(height):
        for c in range(width):
            if grid[r][c] != 0 and not visited[r][c]:
                comp = dfs(r, c, grid[r][c])
                components.append((grid[r][c], comp))

    from collections import defaultdict
    shape_to_comps = defaultdict(list)
    for color, pos_list in components:
        if not pos_list:
            continue
        min_r = min(rr for rr, cc in pos_list)
        min_c = min(cc for rr, cc in pos_list)
        sig = frozenset((rr - min_r, cc - min_c) for rr, cc in pos_list)
        shape_to_comps[sig].append((color, pos_list))

    for sig, complist in shape_to_comps.items():
        if len(complist) == 2:
            c1, pos1 = complist[0]
            c2, pos2 = complist[1]
            if c1 == 1 and c2 != 1:
                for rr, cc in pos1:
                    output[rr][cc] = c2
            elif c2 == 1 and c1 != 1:
                for rr, cc in pos2:
                    output[rr][cc] = c1

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
