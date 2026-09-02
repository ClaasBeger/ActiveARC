"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: d19f7514
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[436](id=436)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0436__d19f7514
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    h = len(grid) // 2
    w = len(grid[0]) if grid else 0
    output = []
    for i in range(h):
        row = []
        for j in range(w):
            top_val = grid[i][j]
            bot_val = grid[i + h][j]
            if top_val == 3 or bot_val == 5:
                row.append(4)
            else:
                row.append(0)
        output.append(row)
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
