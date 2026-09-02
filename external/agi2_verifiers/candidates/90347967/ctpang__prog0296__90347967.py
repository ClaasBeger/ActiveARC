"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 90347967
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[296](id=296)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0296__90347967
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    rows, cols = grid.shape
    # Find the gray cell position
    gray_positions = np.argwhere(grid == 5)
    center_r, center_c = gray_positions[0]
    # Create output grid initialized to 0
    output = np.zeros((rows, cols), dtype=int)
    # For each non-zero cell, compute new position and set color
    for r in range(rows):
        for c in range(cols):
            color = grid[r, c]
            if color != 0:
                new_r = 2 * center_r - r
                new_c = 2 * center_c - c
                if 0 <= new_r < rows and 0 <= new_c < cols:
                    output[new_r, new_c] = color
    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
