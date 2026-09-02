"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: f3e62deb
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[522](id=522)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0522__f3e62deb
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    height, width = grid.shape
    shape_size = 3
    max_row = height - shape_size
    max_col = width - shape_size

    # Find the ring position and color
    nonzero = np.argwhere(grid != 0)
    colors = np.unique(grid[nonzero[:, 0], nonzero[:, 1]])
    if len(colors) != 1:
        raise ValueError("Expected exactly one non-zero color")
    C = colors[0]
    min_r = np.min(nonzero[:, 0])
    min_c = np.min(nonzero[:, 1])
    max_r = np.max(nonzero[:, 0])
    max_c = np.max(nonzero[:, 1])
    if max_r - min_r != shape_size - 1 or max_c - min_c != shape_size - 1:
        raise ValueError("Shape is not 3x3")

    # Direction map
    direction_map = {
        6: 'up',
        4: 'down',
        8: 'right',
        3: 'left'
    }
    if C not in direction_map:
        raise ValueError("Unknown color")
    dir = direction_map[C]

    # Compute new position
    if dir == 'up':
        new_min_r = 0
        new_min_c = min_c
    elif dir == 'down':
        new_min_r = max_row
        new_min_c = min_c
    elif dir == 'right':
        new_min_r = min_r
        new_min_c = max_col
    elif dir == 'left':
        new_min_r = min_r
        new_min_c = 0

    # Create output by copying grid and moving the shape
    output = grid.copy()
    # Clear old position (border only)
    for dr in range(shape_size):
        for dc in range(shape_size):
            if not (dr == 1 and dc == 1):
                output[min_r + dr, min_c + dc] = 0
    # Set new position (border only, center remains 0)
    for dr in range(shape_size):
        for dc in range(shape_size):
            if not (dr == 1 and dc == 1):
                output[new_min_r + dr, new_min_c + dc] = C

    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
