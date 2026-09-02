"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: a680ac02
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[350](id=350)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0350__a680ac02
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []

    rows = len(grid)
    cols = len(grid[0])
    hollows = []

    for i in range(rows - 3):
        for j in range(cols - 3):
            # Extract the 4x4 block
            block = [grid[i + x][j + y] for x in range(4) for y in range(4)]
            # Border positions (all except inner 2x2)
            border = [block[x * 4 + y] for x in range(4) for y in range(4)
                      if not (1 <= x <= 2 and 1 <= y <= 2)]
            inner = [block[x * 4 + y] for x in range(1, 3) for y in range(1, 3)]

            border_colors = set(border)
            if len(border_colors) == 1 and 0 not in border_colors and all(v == 0 for v in inner):
                c = list(border_colors)[0]
                hollows.append({'min_r': i, 'min_c': j, 'color': c})

    if not hollows:
        return []

    # Compute overall bounding box spans
    min_r_all = min(h['min_r'] for h in hollows)
    max_r_all = max(h['min_r'] + 3 for h in hollows)
    min_c_all = min(h['min_c'] for h in hollows)
    max_c_all = max(h['min_c'] + 3 for h in hollows)
    height = max_r_all - min_r_all + 1
    width = max_c_all - min_c_all + 1

    vertical = height > width

    if vertical:
        hollows.sort(key=lambda h: (h['min_r'], h['min_c']))
    else:
        hollows.sort(key=lambda h: (h['min_c'], h['min_r']))

    def get_shape(color):
        return [
            [color, color, color, color],
            [color, 0, 0, color],
            [color, 0, 0, color],
            [color, color, color, color]
        ]

    if vertical:
        out = []
        for h in hollows:
            out.extend(get_shape(h['color']))
        return out
    else:
        num = len(hollows)
        out = [[0] * (4 * num) for _ in range(4)]
        for idx, h in enumerate(hollows):
            sh = get_shape(h['color'])
            for r in range(4):
                out[r][idx * 4:idx * 4 + 4] = sh[r]
        return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
