"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 2601afb7
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[75](id=75)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0075__2601afb7
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    n = len(grid)
    bars = []
    for c in range(n):
        if grid[n-1][c] == 7:
            continue
        color = grid[n-1][c]
        h = 1
        r = n - 2
        while r >= 0 and grid[r][c] == color:
            h += 1
            r -= 1
        bars.append((c, color, h))
    colors = [b[1] for b in bars]
    heights = [b[2] for b in bars]
    if not bars:
        return [row[:] for row in grid]
    new_colors = colors[-1:] + colors[:-1]
    new_heights = heights[1:] + heights[:1]
    new_grid = [row[:] for row in grid]
    # Clear old bars
    for c, _, h in bars:
        for rr in range(n - h, n):
            new_grid[rr][c] = 7
    # Place new bars
    for i in range(len(bars)):
        c = bars[i][0]
        color = new_colors[i]
        h = new_heights[i]
        for rr in range(n - h, n):
            new_grid[rr][c] = color
    return new_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
