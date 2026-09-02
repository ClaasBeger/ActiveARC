"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: fc4aaf52
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[532](id=532)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0532__fc4aaf52
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    output = [row[:] for row in grid]
    rows = len(grid)
    cols = len(grid[0])

    # Find positions where != 8
    positions = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] != 8]
    if not positions:
        return output

    min_r = min(r for r, c in positions)
    max_r = max(r for r, c in positions)
    height = max_r - min_r + 1
    half = height // 2
    upper_min = min_r
    upper_max = min_r + half - 1
    lower_min = min_r + half
    lower_max = max_r

    # Count non-8 in upper_max row for shift
    count_row = upper_max
    shift = sum(1 for c in range(cols) if grid[count_row][c] != 8)

    # Find unique colors
    colors = set(grid[r][c] for r, c in positions)
    c1, c2 = list(colors)
    swap = {c1: c2, c2: c1}

    # Apply swap to lower half
    for r in range(lower_min, lower_max + 1):
        for c in range(cols):
            if grid[r][c] != 8:
                output[r][c] = swap[grid[r][c]]

    # Clear original upper half positions
    for r in range(upper_min, upper_max + 1):
        for c in range(cols):
            if grid[r][c] != 8:
                output[r][c] = 8

    # Move swapped upper half right by shift
    for r in range(upper_min, upper_max + 1):
        for c in range(cols):
            if grid[r][c] != 8:
                new_c = c + shift
                if 0 <= new_c < cols:
                    output[r][new_c] = swap[grid[r][c]]

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
