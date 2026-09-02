"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 310f3251
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[92](id=92)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0092__310f3251
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    h = len(grid)
    w = len(grid[0])
    out_h = 3 * h
    out_w = 3 * w
    out = [[0 for _ in range(out_w)] for _ in range(out_h)]
    for r in range(out_h):
        for c in range(out_w):
            out[r][c] = grid[r % h][c % w]
    for r in range(out_h):
        for c in range(out_w):
            src_color = grid[(r + 1) % h][(c + 1) % w]
            if src_color != 0 and out[r][c] == 0:
                out[r][c] = 2
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
