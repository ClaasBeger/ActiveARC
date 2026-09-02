"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: dce56571
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[466](id=466)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0466__dce56571
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    # Find C and N
    N = 0
    C = -1
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 8:
                if C == -1:
                    C = grid[r][c]
                N += 1
    # Middle row
    mid = rows // 2
    # Left padding
    left = (cols - N) // 2
    # Create output
    output = [[8 for _ in range(cols)] for _ in range(rows)]
    # Set the line
    for i in range(N):
        output[mid][left + i] = C
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
