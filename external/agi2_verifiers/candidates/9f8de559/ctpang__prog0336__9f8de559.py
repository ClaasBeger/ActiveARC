"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9f8de559
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[336](id=336)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0336__9f8de559
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = [row[:] for row in grid]  # copy
    rows = len(grid)
    cols = len(grid[0])

    # Find red (2)
    red_i, red_j = None, None
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 2:
                red_i, red_j = i, j
                break
        if red_i is not None:
            break

    if red_i is None:
        return grid  # No red, no change

    # Find adjacent pink (6), 8-connected
    neighbors = []
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            ni = red_i + di
            nj = red_j + dj
            if 0 <= ni < rows and 0 <= nj < cols and grid[ni][nj] == 6:
                neighbors.append((di, dj))

    # Assume exactly one
    if len(neighbors) != 1:
        return grid  # If not, no change or handle differently, but per examples =1

    dr, dc = neighbors[0]
    ext_dr = -dr
    ext_dc = -dc

    # Move in extension direction
    cur_i = red_i + ext_dr
    cur_j = red_j + ext_dc
    while 0 <= cur_i < rows and 0 <= cur_j < cols and grid[cur_i][cur_j] == 7:
        cur_i += ext_dr
        cur_j += ext_dc

    # Change the first non-7 to 7
    if 0 <= cur_i < rows and 0 <= cur_j < cols and grid[cur_i][cur_j] != 7:
        grid[cur_i][cur_j] = 7

    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
