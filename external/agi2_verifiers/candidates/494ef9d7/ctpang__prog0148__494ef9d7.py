"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 494ef9d7
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[148](id=148)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0148__494ef9d7
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    output = [row[:] for row in grid]
    pairs = [{1, 8}, {4, 7}]
    for r in range(len(grid)):
        colored = [(c, grid[r][c]) for c in range(len(grid[0])) if grid[r][c] != 0]
        if len(colored) == 2:
            left_pos, left_col = colored[0]
            right_pos, right_col = colored[1]
            if set([left_col, right_col]) in pairs:
                target = left_pos + 1
                if target != right_pos:
                    output[r][target] = right_col
                    output[r][right_pos] = 0
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
