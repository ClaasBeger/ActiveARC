"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: bcb3040b
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[398](id=398)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0398__bcb3040b
"""
from __future__ import annotations



import numpy as np

def get_line_points(r0, c0, r1, c1):
    points = []
    dx = abs(c1 - c0)
    dy = abs(r1 - r0)
    r = r0
    c = c0
    sr = 1 if r0 < r1 else -1
    sc = 1 if c0 < c1 else -1
    if dx > dy:
        err = dx // 2
        for _ in range(dx + 1):
            points.append((r, c))
            err -= dy
            if err < 0:
                r += sr
                err += dx
            c += sc
    else:
        err = dy // 2
        for _ in range(dy + 1):
            points.append((r, c))
            err -= dx
            if err < 0:
                c += sc
                err += dy
            r += sr
    return points

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    red_positions = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                red_positions.append((r, c))
    if len(red_positions) != 2:
        return [row[:] for row in grid]
    (r1, c1), (r2, c2) = red_positions
    points = get_line_points(r1, c1, r2, c2)
    output = [row[:] for row in grid]
    for r, c in points:
        if output[r][c] == 0:
            output[r][c] = 2
        elif output[r][c] == 1:
            output[r][c] = 3
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
