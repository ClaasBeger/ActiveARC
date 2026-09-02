"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 50a16a69
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[161](id=161)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0161__50a16a69
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    h = len(grid)
    w = len(grid[0])
    # Assume bottom row is uniform
    b = grid[h-1][0]
    # Collect s for row 0
    s = []
    for col in range(w):
        if grid[0][col] != b:
            s.append(grid[0][col])
        else:
            break
    l = len(s)
    # Find minimal p
    p = None
    for pp in range(1, l + 1):
        unit = s[0:pp]
        if all(s[i] == unit[i % pp] for i in range(l)):
            p = pp
            break
    c = s[0:p]
    # For row 0, d_even = 0
    d_even = 0
    # Collect s_odd for row 1 (if h > 1)
    if h > 1:
        s_odd = []
        for col in range(w):
            if grid[1][col] != b:
                s_odd.append(grid[1][col])
            else:
                break
        l_odd = len(s_odd)
        # Find d_odd
        d_odd = None
        for d in range(p):
            if all(s_odd[i] == c[(i + d) % p] for i in range(l_odd)):
                d_odd = d
                break
    else:
        d_odd = (d_even + 1) % p  # If only one row, but unlikely
    # Now create output
    output = [[0] * w for _ in range(h)]
    for r in range(h):
        if r % 2 == 0:
            start_d = (d_even + 1) % p
        else:
            start_d = (d_odd + 1) % p
        for col in range(w):
            output[r][col] = c[(col + start_d) % p]
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
