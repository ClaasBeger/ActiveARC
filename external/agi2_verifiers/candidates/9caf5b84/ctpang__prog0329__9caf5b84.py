"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9caf5b84
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[329](id=329)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0329__9caf5b84
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    count = [0] * 10
    for row in grid:
        for cell in row:
            count[cell] += 1
    color_freq = [(i, count[i]) for i in range(10)]
    sorted_colors = sorted(color_freq, key=lambda x: x[1], reverse=True)
    kept = {sorted_colors[0][0], sorted_colors[1][0]}
    output = [row[:] for row in grid]
    for i in range(rows):
        for j in range(cols):
            if output[i][j] not in kept:
                output[i][j] = 7
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
