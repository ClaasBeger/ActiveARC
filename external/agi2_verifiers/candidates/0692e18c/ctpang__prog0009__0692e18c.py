"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 0692e18c
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[9](id=9)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0009__0692e18c
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    n = len(grid)
    # Find the color
    color = 0
    for row in grid:
        for c in row:
            if c != 0:
                color = c
                break
        if color != 0:
            break
    # Create inverse grid
    inverse = [[color if grid[i][j] == 0 else 0 for j in range(n)] for i in range(n)]
    # Create output grid
    out_n = 3 * n
    output = [[0] * out_n for _ in range(out_n)]
    # Place inverse in activated blocks
    for i in range(n):
        for j in range(n):
            if grid[i][j] != 0:
                for di in range(n):
                    for dj in range(n):
                        output[3 * i + di][3 * j + dj] = inverse[di][dj]
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
