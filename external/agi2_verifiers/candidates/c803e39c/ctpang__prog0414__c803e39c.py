"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: c803e39c
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[414](id=414)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0414__c803e39c
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    n = rows - 2

    # Find separator columns from top row
    seps = [c for c in range(cols) if grid[0][c] == 5]

    # Starts and ends for each shape
    starts = [0] + [seps[i] + 1 for i in range(len(seps))]
    ends = [seps[0] - 1 if seps else cols - 1] + [seps[i + 1] - 1 for i in range(len(seps) - 1)] + [cols - 1]

    # Function to extract presence matrix for a shape
    def get_presence(shape_idx):
        s = starts[shape_idx]
        e = ends[shape_idx]
        presence = [[0] * n for _ in range(n)]
        for r in range(n):
            for cc in range(n):
                global_c = s + 1 + cc
                if global_c <= e:
                    val = grid[r + 1][global_c]
                    presence[r][cc] = 1 if val != 0 else 0
                # else remains 0
        return presence

    # Function to get color for a shape
    def get_color(shape_idx):
        s = starts[shape_idx]
        # Find a non-zero cell, starting from s+1
        for r in range(1, rows - 1):
            for cc in range(1, min(n + 1, ends[shape_idx] - s + 1)):
                val = grid[r][s + cc]
                if val != 0:
                    return val
        return 0  # Should not happen

    A = get_presence(0)
    B = get_presence(1)
    fg = get_color(2)
    bg = get_color(3)

    A_np = np.array(A)
    B_np = np.array(B)
    kron = np.kron(B_np, A_np)
    output_np = np.where(kron == 1, fg, bg)
    return output_np.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
