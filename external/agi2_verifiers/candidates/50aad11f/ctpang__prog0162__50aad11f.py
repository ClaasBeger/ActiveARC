"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 50aad11f
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[162](id=162)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0162__50aad11f
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    h = len(grid)
    w = len(grid[0])
    
    def find_components():
        visited = set()
        components = []
        for i in range(h):
            for j in range(w):
                if grid[i][j] == 6 and (i, j) not in visited:
                    comp = []
                    stack = [(i, j)]
                    visited.add((i, j))
                    while stack:
                        r, c = stack.pop()
                        comp.append((r, c))
                        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == 6 and (nr, nc) not in visited:
                                visited.add((nr, nc))
                                stack.append((nr, nc))
                    components.append(comp)
        return components
    
    components = find_components()
    
    seeds = []
    for i in range(h):
        for j in range(w):
            if grid[i][j] != 0 and grid[i][j] != 6:
                seeds.append((i, j, grid[i][j]))
    
    comp_to_info = {}
    for sr, sc, col in seeds:
        min_dist = float('inf')
        assigned_comp = None
        for comp in components:
            this_min = min(abs(r - sr) + abs(c - sc) for r, c in comp)
            if this_min < min_dist:
                min_dist = this_min
                assigned_comp = comp
        comp_to_info[id(assigned_comp)] = (col, sr, sc)
    
    vectors_dx = []
    vectors_dy = []
    for comp in components:
        cid = id(comp)
        color, sr, sc = comp_to_info[cid]
        n = len(comp)
        center_r = sum(r for r, c in comp) / n
        center_c = sum(c for r, c in comp) / n
        dx = sc - center_c
        dy = sr - center_r
        vectors_dx.append(dx)
        vectors_dy.append(dy)
    
    avg_abs_dx = sum(abs(x) for x in vectors_dx) / len(vectors_dx)
    avg_abs_dy = sum(abs(y) for y in vectors_dy) / len(vectors_dy)
    
    if avg_abs_dy > avg_abs_dx:
        stacking = 'horizontal'
        sort_key = lambda c: sum(cc for rr, cc in c) / len(c)
    else:
        stacking = 'vertical'
        sort_key = lambda c: sum(rr for rr, cc in c) / len(c)
    
    sorted_comps = sorted(components, key=sort_key)
    
    small_grids = []
    for comp in sorted_comps:
        cid = id(comp)
        color = comp_to_info[cid][0]
        minr = min(r for r, c in comp)
        minc = min(c for r, c in comp)
        maxr = max(r for r, c in comp)
        maxc = max(c for r, c in comp)
        sh = maxr - minr + 1
        sw = maxc - minc + 1
        sg = [[0] * sw for _ in range(sh)]
        for r, c in comp:
            sg[r - minr][c - minc] = color
        small_grids.append(sg)
    
    if stacking == 'horizontal':
        if not small_grids:
            return []
        out_h = max(len(sg) for sg in small_grids)
        out_w = sum(len(sg[0]) for sg in small_grids)
        out = [[0] * out_w for _ in range(out_h)]
        cur = 0
        for sg in small_grids:
            sh = len(sg)
            sw = len(sg[0])
            for i in range(sh):
                for j in range(sw):
                    out[i][cur + j] = sg[i][j]
            cur += sw
    else:
        if not small_grids:
            return []
        out_w = max(len(sg[0]) for sg in small_grids)
        out_h = sum(len(sg) for sg in small_grids)
        out = [[0] * out_w for _ in range(out_h)]
        cur = 0
        for sg in small_grids:
            sh = len(sg)
            sw = len(sg[0])
            for i in range(sh):
                for j in range(sw):
                    out[cur + i][j] = sg[i][j]
            cur += sh
    
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
