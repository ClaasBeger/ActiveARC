"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 22208ba4
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[60](id=60)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0060__22208ba4
"""
from __future__ import annotations



import numpy as np

from collections import defaultdict

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
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
    color_to_comps = defaultdict(list)
    for colr, comp in components:
        color_to_comps[colr].append(comp)
    output = [row[:] for row in grid]
    for colr, comps in color_to_comps.items():
        if len(comps) <= 1:
            continue
        for comp in comps:
            for r, c in comp:
                output[r][c] = 7
        for comp in comps:
            if not comp:
                continue
            min_r = min(rr for rr, cc in comp)
            max_r = max(rr for rr, cc in comp)
            min_c = min(cc for rr, cc in comp)
            max_c = max(cc for rr, cc in comp)
            height = max_r - min_r + 1
            width = max_c - min_c + 1
            dr = 0
            dc = 0
            if min_r == 0:
                dr += height
            if max_r == rows - 1:
                dr -= height
            if min_c == 0:
                dc += width
            if max_c == cols - 1:
                dc -= width
            for rr, cc in comp:
                new_r = rr + dr
                new_c = cc + dc
                if 0 <= new_r < rows and 0 <= new_c < cols:
                    output[new_r][new_c] = colr
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
