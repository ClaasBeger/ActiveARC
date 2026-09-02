"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: edcc2ff0
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[515](id=515)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0515__edcc2ff0
"""
from __future__ import annotations



import numpy as np

import collections

def transform(grid: list[list[int]]) -> list[list[int]]:
    output = [row[:] for row in grid]
    rows = len(grid)
    cols = len(grid[0])
    bg = grid[7][0]
    kept = set()
    seed_rows = {}
    for r in [1, 3, 5]:
        color = grid[r][0]
        if color != 0:
            kept.add(color)
            seed_rows[color] = r
    visited = [[False] * cols for _ in range(rows)]
    counts = {}
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for r in range(7, rows):
        for c in range(cols):
            if grid[r][c] != bg and not visited[r][c]:
                color = grid[r][c]
                component = []
                queue = collections.deque([(r, c)])
                visited[r][c] = True
                while queue:
                    cr, cc = queue.popleft()
                    component.append((cr, cc))
                    for dr, dc in directions:
                        nr, nc = cr + dr, cc + dc
                        if 7 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            queue.append((nr, nc))
                if color not in kept:
                    for pr, pc in component:
                        output[pr][pc] = bg
                else:
                    counts[color] = counts.get(color, 0) + 1
    for color, srow in seed_rows.items():
        count = counts.get(color, 0)
        if count == 0:
            output[srow][0] = 0
        else:
            for j in range(count):
                output[srow][j] = color
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
