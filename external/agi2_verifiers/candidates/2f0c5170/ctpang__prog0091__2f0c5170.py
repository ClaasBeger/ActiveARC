"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 2f0c5170
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[91](id=91)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0091__2f0c5170
"""
from __future__ import annotations



import numpy as np

from collections import deque, defaultdict

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    visited = set()
    components = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 8 and (r, c) not in visited:
                component = set()
                q = deque([(r, c)])
                visited.add((r, c))
                while q:
                    cr, cc = q.popleft()
                    component.add((cr, cc))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 8 and (nr, nc) not in visited:
                            visited.add((nr, nc))
                            q.append((nr, nc))
                components.append(component)
    # Assume exactly two components
    small_local = None
    large_local = None
    dot_s_r, dot_s_c = None, None
    dot_l_r, dot_l_c = None, None
    small_h, small_w = None, None
    large_h, large_w = None, None
    for comp in components:
        min_r = min(rr for rr, _ in comp)
        max_r = max(rr for rr, _ in comp)
        min_c = min(cc for _, cc in comp)
        max_c = max(cc for _, cc in comp)
        h = max_r - min_r + 1
        w = max_c - min_c + 1
        local = [[grid[min_r + i][min_c + j] for j in range(w)] for i in range(h)]
        num_col = sum(1 for roww in local for cell in roww if cell != 0)
        if num_col == 1:
            small_local = local
            small_h = h
            small_w = w
            for ii in range(h):
                for jj in range(w):
                    if local[ii][jj] != 0:
                        dot_s_r = ii
                        dot_s_c = jj
                        break
                else:
                    continue
                break
        else:
            large_local = local
            large_h = h
            large_w = w
            freq = defaultdict(int)
            for ii in range(h):
                for jj in range(w):
                    if local[ii][jj] != 0:
                        freq[local[ii][jj]] += 1
            once_colors = [col for col, cnt in freq.items() if cnt == 1]
            dot_color = once_colors[0]  # Assume exactly one
            for ii in range(h):
                for jj in range(w):
                    if local[ii][jj] == dot_color:
                        dot_l_r = ii
                        dot_l_c = jj
                        break
                else:
                    continue
                break
    offset_r = dot_s_r - dot_l_r
    offset_c = dot_s_c - dot_l_c
    output = [[0] * small_w for _ in range(small_h)]
    for i in range(small_h):
        for j in range(small_w):
            i_l = i - offset_r
            j_l = j - offset_c
            if 0 <= i_l < large_h and 0 <= j_l < large_w:
                output[i][j] = large_local[i_l][j_l]
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
