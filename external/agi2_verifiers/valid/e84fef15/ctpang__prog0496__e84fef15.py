"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e84fef15
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[496](id=496)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0496__e84fef15
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    starts = [0, 6, 12, 18, 24]
    output = [[0 for _ in range(5)] for _ in range(5)]
    for i in range(5):
        for j in range(5):
            colors = set()
            for k in range(5):
                for l in range(5):
                    r = starts[k] + i
                    c = starts[l] + j
                    colors.add(grid[r][c])
            if len(colors) == 1:
                output[i][j] = next(iter(colors))
            else:
                output[i][j] = 1
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
