"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 996ec1f3
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[321](id=321)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0321__996ec1f3
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    g = np.array(grid)
    height, width = g.shape

    # Find uniform row
    horiz_cross = None
    cross_color = None
    for r in range(height):
        if np.all(g[r] == g[r, 0]):
            horiz_cross = r
            cross_color = g[r, 0]
            break  # Assuming unique

    # Find uniform column with cross_color
    vert_cross = None
    for c in range(width):
        if np.all(g[:, c] == cross_color):
            vert_cross = c
            break  # Assuming unique

    # Function to get most frequent color
    def most_frequent(subgrid):
        if subgrid.size == 0:
            return 0
        counts = np.bincount(subgrid.ravel(), minlength=10)
        return np.argmax(counts)

    # Quadrants
    tl = g[0:horiz_cross, 0:vert_cross]
    tr = g[0:horiz_cross, vert_cross + 1 : width]
    bl = g[horiz_cross + 1 : height, 0:vert_cross]
    br = g[horiz_cross + 1 : height, vert_cross + 1 : width]

    tl_color = most_frequent(tl)
    tr_color = most_frequent(tr)
    bl_color = most_frequent(bl)
    br_color = most_frequent(br)

    output = [
        [tl_color, cross_color, tr_color],
        [cross_color, cross_color, cross_color],
        [bl_color, cross_color, br_color],
    ]
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
