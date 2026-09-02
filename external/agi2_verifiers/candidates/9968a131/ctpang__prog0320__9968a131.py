"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9968a131
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[320](id=320)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0320__9968a131
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    rows = len(grid)
    cols = len(grid[0])
    background = grid[0][cols - 1]
    min_col = cols
    max_col = -1
    for c in range(cols):
        for r in range(rows):
            if grid[r][c] != background:
                min_col = min(min_col, c)
                max_col = max(max_col, c)
    if max_col < 0:
        return [row[:] for row in grid]
    w = max_col - min_col + 1
    standard = None
    for r in range(rows):
        has_non = any(grid[r][c] != background for c in range(min_col, max_col + 1))
        if has_non:
            standard = [grid[r][c] for c in range(min_col, max_col + 1)]
            break
    if standard is None:
        return [row[:] for row in grid]
    output = [row[:] for row in grid]
    rev_standard = standard[::-1]
    for r in range(rows):
        current = [grid[r][c] for c in range(min_col, max_col + 1)]
        if current == rev_standard:
            start_c = min_col
            segment_length = w + 1
            if start_c + segment_length > cols:
                continue  # Safeguard, though not needed in examples
            segment = [grid[r][c] for c in range(start_c, start_c + segment_length)]
            new_segment = [segment[-1]] + segment[:-1]
            for i in range(segment_length):
                output[r][start_c + i] = new_segment[i]
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
