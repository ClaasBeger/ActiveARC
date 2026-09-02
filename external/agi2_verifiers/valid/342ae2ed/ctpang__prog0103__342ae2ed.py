"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 342ae2ed
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[103](id=103)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0103__342ae2ed
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    output = [row[:] for row in grid]
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right

    components = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 7 and not visited[r][c]:
                color = grid[r][c]
                component = []
                min_r, max_r = r, r
                min_c, max_c = c, c
                stack = [(r, c)]
                visited[r][c] = True
                while stack:
                    cr, cc = stack.pop()
                    component.append((cr, cc))
                    min_r = min(min_r, cr)
                    max_r = max(max_r, cr)
                    min_c = min(min_c, cc)
                    max_c = max(max_c, cc)
                    for dr, dc in directions:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                components.append({
                    'color': color,
                    'min_r': min_r,
                    'max_r': max_r,
                    'min_c': min_c,
                    'max_c': max_c
                })

    from collections import defaultdict
    color_to_comps = defaultdict(list)
    for comp in components:
        color_to_comps[comp['color']].append(comp)

    for color, comps in color_to_comps.items():
        if len(comps) == 2:
            comps.sort(key=lambda x: x['min_r'])
            upper = comps[0]
            lower = comps[1]
            row_diff = lower['min_r'] - upper['max_r']
            if row_diff <= 0:
                continue

            options = [
                ('br_tl', upper['max_c'], lower['min_c']),
                ('bl_tr', upper['min_c'], lower['max_c'])
            ]
            for _, s_c, e_c in options:
                if abs(s_c - e_c) == row_diff:
                    start_r = upper['max_r']
                    start_c = s_c
                    end_c = e_c
                    dy = 1 if end_c > start_c else -1
                    for i in range(1, row_diff):
                        nr = start_r + i
                        nc = start_c + i * dy
                        output[nr][nc] = color
                    break

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
