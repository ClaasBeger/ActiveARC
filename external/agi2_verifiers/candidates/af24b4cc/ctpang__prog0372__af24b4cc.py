"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: af24b4cc
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[372](id=372)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0372__af24b4cc
"""
from __future__ import annotations



import numpy as np

import collections

def transform(grid: list[list[int]]) -> list[list[int]]:
    # Define block positions: (row_start, row_end, col_start, col_end)
    blocks = [
        (1, 3, 1, 2),  # top left
        (1, 3, 4, 5),  # top middle
        (1, 3, 7, 8),  # top right
        (5, 7, 1, 2),  # bottom left
        (5, 7, 4, 5),  # bottom middle
        (5, 7, 7, 8),  # bottom right
    ]
    
    modes = []
    for rs, re, cs, ce in blocks:
        vals = []
        for i in range(rs, re + 1):
            for j in range(cs, ce + 1):
                vals.append(grid[i][j])
        counter = collections.Counter(vals)
        mode = counter.most_common(1)[0][0]
        modes.append(mode)
    
    # Build output grid
    output = [
        [0, 0, 0, 0, 0],
        [0, modes[0], modes[1], modes[2], 0],
        [0, modes[3], modes[4], modes[5], 0],
        [0, 0, 0, 0, 0]
    ]
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
