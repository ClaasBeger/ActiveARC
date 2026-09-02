"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 60a26a3e
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[197](id=197)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0197__60a26a3e
"""
from __future__ import annotations



import numpy as np

import copy
from collections import defaultdict

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []

    rows = len(grid)
    cols = len(grid[0])

    # Find centers
    centers = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                has_up = (r > 0 and grid[r-1][c] == 2)
                has_down = (r < rows-1 and grid[r+1][c] == 2)
                has_left = (c > 0 and grid[r][c-1] == 2)
                has_right = (c < cols-1 and grid[r][c+1] == 2)
                if has_up and has_down and has_left and has_right:
                    centers.append((r, c))

    # Group for horizontal: row to list of c
    hor_groups = defaultdict(list)
    for r, c in centers:
        hor_groups[r].append(c)

    # Group for vertical: col to list of r
    ver_groups = defaultdict(list)
    for r, c in centers:
        ver_groups[c].append(r)

    # Copy grid
    out = copy.deepcopy(grid)

    # Horizontal fills
    for r, clist in hor_groups.items():
        if len(clist) >= 2:
            clist.sort()
            for i in range(len(clist) - 1):
                left_c = clist[i]
                right_c = clist[i + 1]
                start_c = left_c + 2
                end_c = right_c - 2
                for cc in range(start_c, end_c + 1):
                    if 0 <= cc < cols and out[r][cc] == 0:
                        out[r][cc] = 1

    # Vertical fills
    for c, rlist in ver_groups.items():
        if len(rlist) >= 2:
            rlist.sort()
            for i in range(len(rlist) - 1):
                upper_r = rlist[i]
                lower_r = rlist[i + 1]
                start_r = upper_r + 2
                end_r = lower_r - 2
                for rr in range(start_r, end_r + 1):
                    if 0 <= rr < rows and out[rr][c] == 0:
                        out[rr][c] = 1

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
