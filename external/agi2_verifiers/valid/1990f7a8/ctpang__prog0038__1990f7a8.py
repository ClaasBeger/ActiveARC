"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 1990f7a8
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[38](id=38)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0038__1990f7a8
"""
from __future__ import annotations



import numpy as np

from collections import deque

def transform(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def bfs(start_r, start_c):
        component = []
        queue = deque([(start_r, start_c)])
        visited[start_r][start_c] = True
        while queue:
            r, c = queue.popleft()
            component.append((r, c))
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == 2:
                    visited[nr][nc] = True
                    queue.append((nr, nc))
        return component

    components = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2 and not visited[r][c]:
                comp = bfs(r, c)
                components.append(comp)

    comps_sorted = sorted(components, key=lambda comp: min(r for r, c in comp))

    top_comps = comps_sorted[:2]
    bottom_comps = comps_sorted[2:]

    def get_min_c(comp):
        return min(c for r, c in comp)

    top_left_comp = sorted(top_comps, key=get_min_c)[0]
    top_right_comp = sorted(top_comps, key=get_min_c)[1]
    bottom_left_comp = sorted(bottom_comps, key=get_min_c)[0]
    bottom_right_comp = sorted(bottom_comps, key=get_min_c)[1]

    def get_pattern(comp):
        min_r = min(r for r, c in comp)
        min_c = min(c for r, c in comp)
        pat = [[0] * 3 for _ in range(3)]
        for r, c in comp:
            pat[r - min_r][c - min_c] = 2
        return pat

    top_left = get_pattern(top_left_comp)
    top_right = get_pattern(top_right_comp)
    bottom_left = get_pattern(bottom_left_comp)
    bottom_right = get_pattern(bottom_right_comp)

    top_rows = []
    for i in range(3):
        top_rows.append(top_left[i] + [0] + top_right[i])

    bottom_rows = []
    for i in range(3):
        bottom_rows.append(bottom_left[i] + [0] + bottom_right[i])

    output = top_rows + [[0] * 7] + bottom_rows
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
