"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 94414823
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[308](id=308)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0308__94414823
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    g = np.array(grid)
    rows, cols = g.shape

    # Find frame bounding box
    frame_pos = np.argwhere(g == 5)
    min_r = frame_pos[:, 0].min()
    max_r = frame_pos[:, 0].max()
    min_c = frame_pos[:, 1].min()
    max_c = frame_pos[:, 1].max()

    # Interior bounds
    int_min_r = min_r + 1
    int_max_r = max_r - 1
    int_min_c = min_c + 1
    int_max_c = max_c - 1
    h = int_max_r - int_min_r + 1
    w = int_max_c - int_min_c + 1
    half_h = h // 2
    half_w = w // 2

    # Find colored cells
    colored = []
    for r in range(rows):
        for c in range(cols):
            colr = g[r, c]
            if colr != 0 and colr != 5:
                colored.append((r, c, colr))

    (r1, c1, color1), (r2, c2, color2) = colored

    if r1 == r2:
        r = r1
        # Sort by column
        if c1 > c2:
            c1, c2 = c2, c1
            color1, color2 = color2, color1
        left_color = color1
        right_color = color2
        if r < min_r:
            side = 'top'
        elif r > max_r:
            side = 'bottom'
        else:
            raise ValueError("Invalid side")
        if side == 'top':
            top_left_color = left_color
            top_right_color = right_color
            bot_left_color = right_color
            bot_right_color = left_color
        else:  # bottom
            bot_left_color = left_color
            bot_right_color = right_color
            top_left_color = right_color
            top_right_color = left_color
    elif c1 == c2:
        c = c1
        # Sort by row
        if r1 > r2:
            r1, r2 = r2, r1
            color1, color2 = color2, color1
        top_color = color1
        bot_color = color2
        if c < min_c:
            side = 'left'
        elif c > max_c:
            side = 'right'
        else:
            raise ValueError("Invalid side")
        if side == 'left':
            top_left_color = top_color
            bot_left_color = bot_color
            top_right_color = bot_color
            bot_right_color = top_color
        else:  # right
            top_right_color = top_color
            bot_right_color = bot_color
            top_left_color = bot_color
            bot_left_color = top_color
    else:
        raise ValueError("Colored cells not on same row or column")

    # Fill top half
    for rr in range(int_min_r, int_min_r + half_h):
        for cc in range(int_min_c, int_min_c + half_w):
            g[rr, cc] = top_left_color
        for cc in range(int_min_c + half_w, int_min_c + w):
            g[rr, cc] = top_right_color

    # Fill bottom half
    for rr in range(int_min_r + half_h, int_min_r + h):
        for cc in range(int_min_c, int_min_c + half_w):
            g[rr, cc] = bot_left_color
        for cc in range(int_min_c + half_w, int_min_c + w):
            g[rr, cc] = bot_right_color

    return g.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
