"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9f41bd9c
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[334](id=334)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0334__9f41bd9c
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    height = len(grid)
    width = len(grid[0])

    # Find pink_start
    pink_start = None
    for r in range(height):
        if all(cell == 6 for cell in grid[r]):
            pink_start = r
            break

    # Find structure cells
    structure_cells = [(rr, cc) for rr in range(pink_start) for cc in range(width) if grid[rr][cc] == 5]

    rows = [rr for rr, cc in structure_cells]
    min_r = min(rows)
    max_r = max(rows)

    cols = [cc for rr, cc in structure_cells]
    min_c = min(cols)
    max_c = max(cols)
    w = max_c - min_c + 1
    original_start = min_c

    # Find top_h
    top_h = 0
    for r in range(min_r, max_r + 1):
        if all(grid[r][c] == 5 for c in range(original_start, original_start + w)):
            top_h += 1
        else:
            break

    pillar_h = (max_r - min_r + 1) - top_h

    # Determine new_start and shift_dir
    if original_start == 0:
        new_start = width - w
        shift_dir = -1
    else:
        new_start = 0
        shift_dir = 1

    # Create output
    output = [row[:] for row in grid]

    # Clear old structure
    for rr, cc in structure_cells:
        output[rr][cc] = 1

    # Place new structure
    for r in range(min_r, min_r + top_h):
        for c in range(new_start, new_start + w):
            output[r][c] = 5

    for i in range(pillar_h):
        r = min_r + top_h + i
        shift = shift_dir * i
        base = new_start + shift
        for rel in [0, 2, 4]:
            cc = base + rel
            if 0 <= cc < width:
                output[r][cc] = 5

    # Place brown
    if pillar_h > 0:
        lowest_i = pillar_h - 1
        lowest_base = new_start + shift_dir * lowest_i
        if shift_dir > 0:
            lowest_left = lowest_base + 0
            brown_start = lowest_left + 1
            brown_end = width - 1
        else:
            lowest_right = lowest_base + 4
            brown_start = 0
            brown_end = lowest_right - 1
        for c in range(max(0, brown_start), min(width - 1, brown_end) + 1):
            output[pink_start][c] = 9

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
