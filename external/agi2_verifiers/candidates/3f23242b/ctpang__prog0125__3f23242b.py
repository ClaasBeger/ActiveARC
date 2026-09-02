"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 3f23242b
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[125](id=125)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0125__3f23242b
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    output = [row[:] for row in grid]
    rows = len(output)
    cols = len(output[0])
    greens = []
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 3:
                greens.append((i, j))
    for r, c in greens:
        # Row r-2: 5 from c-2 to c+2
        if 0 <= r - 2 < rows:
            for j in range(max(0, c - 2), min(cols, c + 3)):
                output[r - 2][j] = 5
        # Row r-1: 2 at c-2, 5 at c, 2 at c+2
        if 0 <= r - 1 < rows:
            if 0 <= c - 2 < cols:
                output[r - 1][c - 2] = 2
            if 0 <= c < cols:
                output[r - 1][c] = 5
            if 0 <= c + 2 < cols:
                output[r - 1][c + 2] = 2
        # Row r: 2 at c-2, 3 at c (already), 2 at c+2
        if 0 <= r < rows:
            if 0 <= c - 2 < cols:
                output[r][c - 2] = 2
            if 0 <= c + 2 < cols:
                output[r][c + 2] = 2
        # Row r+1: 2 at c-2, 2 at c+2
        if 0 <= r + 1 < rows:
            if 0 <= c - 2 < cols:
                output[r + 1][c - 2] = 2
            if 0 <= c + 2 < cols:
                output[r + 1][c + 2] = 2
        # Row r+2: all 2, except 8 from c-2 to c+2
        if 0 <= r + 2 < rows:
            for j in range(cols):
                output[r + 2][j] = 2
            for j in range(max(0, c - 2), min(cols, c + 3)):
                output[r + 2][j] = 8
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
