"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 11e1fe23
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[24](id=24)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0024__11e1fe23
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = [row[:] for row in grid]  # copy
    rows = len(grid)
    cols = len(grid[0])
    colored = []
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != 0:
                colored.append((i, j, grid[i][j]))
    if not colored:
        return grid
    from collections import defaultdict
    row_count = defaultdict(int)
    row_cols = defaultdict(list)
    for i, j, _ in colored:
        row_count[i] += 1
        row_cols[i].append(j)
    max_count = max(row_count.values())
    if max_count < 2:
        return grid  # No transformation if no row with multiple
    k = max(row_count, key=row_count.get)
    cols_list = sorted(row_cols[k])
    a = cols_list[0]
    b = cols_list[-1]
    c = (a + b) // 2
    d = (b - a) // 2
    candidates = []
    r1 = k - d
    if 0 <= r1 < rows:
        candidates.append(r1)
    r2 = k + d
    if 0 <= r2 < rows:
        candidates.append(r2)
    center_r = None
    center_c = c
    for cand_r in candidates:
        valid = True
        for ri, ci, _ in colored:
            if abs(ri - cand_r) != abs(ci - c):
                valid = False
                break
        if valid:
            center_r = cand_r
            break
    if center_r is None:
        return grid  # No valid center
    # Set grey
    if grid[center_r][center_c] == 0:
        grid[center_r][center_c] = 5
    # Add adjacents
    for ri, ci, col in colored:
        dr = ri - center_r
        dc = ci - center_c
        s_dr = 1 if dr > 0 else -1 if dr < 0 else 0
        s_dc = 1 if dc > 0 else -1 if dc < 0 else 0
        if s_dr == 0 or s_dc == 0:
            continue  # Skip if not diagonal
        add_r = center_r + s_dr
        add_c = center_c + s_dc
        if 0 <= add_r < rows and 0 <= add_c < cols:
            if grid[add_r][add_c] == 0:
                grid[add_r][add_c] = col
    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
