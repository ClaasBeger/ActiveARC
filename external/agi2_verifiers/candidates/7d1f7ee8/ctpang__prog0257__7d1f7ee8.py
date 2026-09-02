"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 7d1f7ee8
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[257](id=257)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0257__7d1f7ee8
"""
from __future__ import annotations



import numpy as np

from collections import deque

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    h = len(grid)
    w = len(grid[0])
    visited = [[False] * w for _ in range(h)]
    comps = []
    for i in range(h):
        for j in range(w):
            if grid[i][j] != 0 and not visited[i][j]:
                color = grid[i][j]
                cells = []
                stack = [(i, j)]
                visited[i][j] = True
                while stack:
                    r, c = stack.pop()
                    cells.append((r, c))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < h and 0 <= nc < w and not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                rep = min(cells)
                comps.append({'cells': cells, 'color': color, 'rep': rep})
    n = len(comps)
    enclose_matrix = [[False] * n for _ in range(n)]
    for ai in range(n):
        A = comps[ai]
        A_set = set(A['cells'])
        for bi in range(n):
            if ai == bi:
                continue
            B = comps[bi]
            rr, cc = B['rep']
            vis = [[False] * w for _ in range(h)]
            q = deque([(rr, cc)])
            vis[rr][cc] = True
            can_escape = False
            while q:
                r, c = q.popleft()
                if r == 0 or r == h - 1 or c == 0 or c == w - 1:
                    can_escape = True
                    break
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < h and 0 <= nc < w and not vis[nr][nc] and (nr, nc) not in A_set:
                        vis[nr][nc] = True
                        q.append((nr, nc))
            if not can_escape:
                enclose_matrix[ai][bi] = True
    parent = [-1] * n
    for bi in range(n):
        enclosers = [ai for ai in range(n) if enclose_matrix[ai][bi]]
        direct = []
        for ai in enclosers:
            is_direct = True
            for ci in enclosers:
                if ci != ai and enclose_matrix[ai][ci] and enclose_matrix[ci][bi]:
                    is_direct = False
                    break
            if is_direct:
                direct.append(ai)
        if direct:
            parent[bi] = direct[0]
    def get_root_color(idx):
        if parent[idx] == -1:
            return comps[idx]['color']
        else:
            return get_root_color(parent[idx])
    for i in range(n):
        new_color = get_root_color(i)
        for r, c in comps[i]['cells']:
            grid[r][c] = new_color
    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
