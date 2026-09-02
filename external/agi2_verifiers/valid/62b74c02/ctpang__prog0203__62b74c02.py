"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 62b74c02
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[203](id=203)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0203__62b74c02
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid:
        return []
    h = len(grid)
    w = len(grid[0])
    # Find k: first column where all cells are 0
    k = w
    for j in range(w):
        if all(grid[i][j] == 0 for i in range(h)):
            k = j
            break
    # Build output
    output = []
    for i in range(h):
        seq = grid[i][:k]
        if k == 0:
            output.append([0] * w)
            continue
        last = seq[-1]
        num_repeats = (w - k) - (k - 1)
        append_part = seq[1:]
        row = seq + [last] * num_repeats + append_part
        output.append(row)
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
