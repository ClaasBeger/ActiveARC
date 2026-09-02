"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: af726779
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[373](id=373)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0373__af726779
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    height = len(grid)
    width = len(grid[0])
    code_row = -1
    for r in range(height):
        if any(cell == 7 for cell in grid[r]):
            code_row = r
            break
    if code_row == -1:
        return grid
    signals = [c for c in range(width) if grid[code_row][c] == 7]
    current_color = 6
    current_row = code_row + 2
    while current_row < height and signals:
        new_signals = []
        for i in range(len(signals) - 1):
            c1 = signals[i]
            c2 = signals[i + 1]
            if c2 - c1 == 2:
                mid = c1 + 1
                grid[current_row][mid] = current_color
                new_signals.append(mid)
        signals = new_signals
        current_color = 13 - current_color
        current_row += 2
    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
