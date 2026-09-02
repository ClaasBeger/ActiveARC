"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 917bccba
source: GitMonsters/SOLVED-562-verified
original_path: solves/917bccba/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__917bccba
"""
from __future__ import annotations



"""
ARC-AGI puzzle 917bccba solver.

Pattern: A grid contains a rectangular border (color A) and a cross/plus shape
(color B) passing through it. The cross interior is erased and its outer arms
are relocated so the vertical arm aligns with the rectangle's right edge and
the horizontal arm aligns with the rectangle's top edge.
"""

import json
import numpy as np
from pathlib import Path


def solve(grid: list[list[int]]) -> list[list[int]]:
    g = np.array(grid)
    rows, cols = g.shape

    # Find the two non-zero colors
    colors = sorted(set(g.flatten()) - {0})

    # Identify the rectangle color: its bounding-box top/bottom rows are fully filled
    rect_color = cross_color = None
    rect_top = rect_bot = rect_left = rect_right = 0
    for color in colors:
        coords = np.argwhere(g == color)
        r_min, c_min = coords.min(axis=0)
        r_max, c_max = coords.max(axis=0)
        if (np.all(g[r_min, c_min:c_max + 1] == color) and
                np.all(g[r_max, c_min:c_max + 1] == color)):
            rect_color = color
            rect_top, rect_bot = int(r_min), int(r_max)
            rect_left, rect_right = int(c_min), int(c_max)
            break

    cross_color = [c for c in colors if c != rect_color][0]

    # Build output: blank grid → rectangle border → relocated cross arms
    out = np.zeros_like(g)

    # Draw rectangle border
    out[rect_top, rect_left:rect_right + 1] = rect_color
    out[rect_bot, rect_left:rect_right + 1] = rect_color
    out[rect_top:rect_bot + 1, rect_left] = rect_color
    out[rect_top:rect_bot + 1, rect_right] = rect_color

    # Vertical cross arm → right edge column, only outside the rectangle
    for r in range(rows):
        if r < rect_top or r > rect_bot:
            out[r, rect_right] = cross_color

    # Horizontal cross arm → top edge row, only outside the rectangle
    for c in range(cols):
        if c < rect_left or c > rect_right:
            out[rect_top, c] = cross_color

    return out.tolist()


# --------------- self-test ---------------

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
