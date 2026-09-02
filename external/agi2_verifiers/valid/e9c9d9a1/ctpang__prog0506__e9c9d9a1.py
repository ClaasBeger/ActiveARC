"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e9c9d9a1
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[506](id=506)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0506__e9c9d9a1
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid:
        return grid
    rows = len(grid)
    cols = len(grid[0])

    # Find horiz_rows: rows where all cells == 3
    horiz_rows = []
    for r in range(rows):
        if all(grid[r][c] == 3 for c in range(cols)):
            horiz_rows.append(r)

    if not horiz_rows:
        return [row[:] for row in grid]

    # Find vert_cols: columns where there exists r not in horiz_rows with grid[r][c] == 3
    vert_cols_set = set()
    for c in range(cols):
        for r in range(rows):
            if grid[r][c] == 3 and r not in horiz_rows:
                vert_cols_set.add(c)
                break
    vert_cols = sorted(list(vert_cols_set))

    if not vert_cols:
        return [row[:] for row in grid]

    # Build regions: list of (start_col, end_col, type) where type='left', 'right', 'center'
    regions = []
    # leftmost
    if vert_cols[0] > 0:
        regions.append((0, vert_cols[0] - 1, 'left'))
    # centers
    for i in range(len(vert_cols) - 1):
        s = vert_cols[i] + 1
        e = vert_cols[i + 1] - 1
        if s <= e:
            regions.append((s, e, 'center'))
    # rightmost
    if vert_cols[-1] < cols - 1:
        s = vert_cols[-1] + 1
        e = cols - 1
        if s <= e:
            regions.append((s, e, 'right'))

    # Make a copy
    output = [row[:] for row in grid]

    # Fill top arm
    top_start = 0
    top_end = horiz_rows[0] - 1
    if top_start <= top_end:
        for reg_start, reg_end, reg_type in regions:
            if reg_type == 'left':
                color = 2
            elif reg_type == 'right':
                color = 4
            else:
                continue
            for r in range(top_start, top_end + 1):
                for c in range(reg_start, reg_end + 1):
                    if output[r][c] == 0:
                        output[r][c] = color

    # Fill bottom arm
    bot_start = horiz_rows[-1] + 1
    bot_end = rows - 1
    if bot_start <= bot_end:
        for reg_start, reg_end, reg_type in regions:
            if reg_type == 'left':
                color = 1
            elif reg_type == 'right':
                color = 8
            else:
                continue
            for r in range(bot_start, bot_end + 1):
                for c in range(reg_start, reg_end + 1):
                    if output[r][c] == 0:
                        output[r][c] = color

    # Fill middle sections
    for i in range(len(horiz_rows) - 1):
        mid_start = horiz_rows[i] + 1
        mid_end = horiz_rows[i + 1] - 1
        if mid_start <= mid_end:
            color = 7
            for reg_start, reg_end, reg_type in regions:
                if reg_type == 'center':
                    for r in range(mid_start, mid_end + 1):
                        for c in range(reg_start, reg_end + 1):
                            if output[r][c] == 0:
                                output[r][c] = color

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
