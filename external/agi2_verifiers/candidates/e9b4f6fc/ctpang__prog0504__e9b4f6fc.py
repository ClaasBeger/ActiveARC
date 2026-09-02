"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e9b4f6fc
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[504](id=504)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0504__e9b4f6fc
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    visited = set()
    components = []

    def dfs(r, c):
        comp = []
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if (cr, cc) in visited:
                continue
            visited.add((cr, cc))
            comp.append((cr, cc))
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 0 and (nr, nc) not in visited:
                    stack.append((nr, nc))
        return comp

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and (r, c) not in visited:
                comp = dfs(r, c)
                components.append(comp)

    if not components:
        return []

    large_comp = max(components, key=len)

    repl = {}
    for comp in components:
        if comp == large_comp:
            continue
        if len(comp) != 2:
            continue
        pos1, pos2 = comp
        if pos1[0] != pos2[0]:
            continue
        if abs(pos1[1] - pos2[1]) != 1:
            continue
        if pos1[1] < pos2[1]:
            left = pos1
            right = pos2
        else:
            left = pos2
            right = pos1
        A = grid[left[0]][left[1]]
        B = grid[right[0]][right[1]]
        repl[B] = A

    rs = [p[0] for p in large_comp]
    cs = [p[1] for p in large_comp]
    min_r = min(rs)
    max_r = max(rs)
    min_c = min(cs)
    max_c = max(cs)
    height = max_r - min_r + 1
    width = max_c - min_c + 1
    output = [[0] * width for _ in range(height)]

    for r, c in large_comp:
        out_r = r - min_r
        out_c = c - min_c
        color = grid[r][c]
        output[out_r][out_c] = repl.get(color, color)

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
