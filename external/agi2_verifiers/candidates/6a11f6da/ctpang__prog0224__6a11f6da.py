"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 6a11f6da
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[224](id=224)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0224__6a11f6da
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    output = [[0 for _ in range(5)] for _ in range(5)]
    for i in range(5):
        for j in range(5):
            k = grid[i + 10][j]
            if k != 0:
                output[i][j] = k
            else:
                b = grid[i][j]
                if b != 0:
                    output[i][j] = b
                else:
                    p = grid[i + 5][j]
                    if p != 0:
                        output[i][j] = p
                    else:
                        output[i][j] = 0
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
