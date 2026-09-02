"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: c074846d
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[406](id=406)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0406__c074846d
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    rows, cols = grid.shape

    # Find grey position
    grey_pos = np.argwhere(grid == 5)
    grey_r, grey_c = grey_pos[0]

    # Collect original red positions
    red_positions = [tuple(pos) for pos in np.argwhere(grid == 2)]

    # Set original reds to 3
    for r, c in red_positions:
        grid[r, c] = 3

    # Set rotated positions to 2
    for r, c in red_positions:
        dr = r - grey_r
        dc = c - grey_c
        new_dr = dc
        new_dc = -dr
        new_r = grey_r + new_dr
        new_c = grey_c + new_dc
        if 0 <= new_r < rows and 0 <= new_c < cols:
            grid[new_r, new_c] = 2

    return grid.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
