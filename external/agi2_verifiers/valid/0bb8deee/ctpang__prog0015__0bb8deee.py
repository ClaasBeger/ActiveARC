"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 0bb8deee
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[15](id=15)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0015__0bb8deee
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    rows, cols = grid.shape

    # Find horizontal row h and color C
    h = None
    C = None
    for i in range(rows):
        if np.all(grid[i] == grid[i, 0]) and grid[i, 0] != 0:
            h = i
            C = grid[i, 0]
            break

    # Find vertical column v with color C
    v = None
    for j in range(cols):
        if np.all(grid[:, j] == C):
            v = j
            break

    # Function to get shape positions and bounding box in a quadrant
    def get_shape(minrow, maxrow, mincol, maxcol):
        pos = []
        for r in range(minrow, maxrow + 1):
            for c in range(mincol, maxcol + 1):
                if grid[r, c] != 0 and grid[r, c] != C:
                    pos.append((r, c, grid[r, c]))
        if not pos:
            return None
        min_r = min(p[0] for p in pos)
        max_r = max(p[0] for p in pos)
        min_c = min(p[1] for p in pos)
        max_c = max(p[1] for p in pos)
        return pos, min_r, max_r, min_c, max_c

    # Get shapes for each quadrant
    ul = get_shape(0, h - 1, 0, v - 1)
    ur = get_shape(0, h - 1, v + 1, cols - 1)
    ll = get_shape(h + 1, rows - 1, 0, v - 1)
    lr = get_shape(h + 1, rows - 1, v + 1, cols - 1)

    # Compute s (max side length across all shapes)
    all_sides = []
    for q in [ul, ur, ll, lr]:
        if q:
            _, mr, Mr, mc, Mc = q
            all_sides.append(Mr - mr + 1)
            all_sides.append(Mc - mc + 1)
    s = max(all_sides) if all_sides else 0

    # Create output grid
    out = np.zeros((2 * s, 2 * s), dtype=int)

    # Function to place shape in output
    def place(pos, min_r, min_c, out_min_r, out_min_c):
        for r, c, col in pos:
            rel_r = r - min_r
            rel_c = c - min_c
            if rel_r < s and rel_c < s:  # In case of padding if sizes differ
                out[out_min_r + rel_r, out_min_c + rel_c] = col

    # Place shapes
    if ul:
        place(ul[0], ul[1], ul[3], 0, 0)
    if ur:
        place(ur[0], ur[1], ur[3], 0, s)
    if ll:
        place(ll[0], ll[1], ll[3], s, 0)
    if lr:
        place(lr[0], lr[1], lr[3], s, s)

    return out.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
