"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ed74f2f2
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[513](id=513)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0513__ed74f2f2
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    g = np.array(grid)
    # Extract left 3x3: rows 1-3, cols 1-3
    left = g[1:4, 1:4]
    # Extract right 3x3: rows 1-3, cols 5-7
    right = g[1:4, 5:8]
    
    # Find extras in left: positions where 5 and not in center column (col 1)
    extras = []
    for r in range(3):
        for c in range(3):
            if left[r, c] == 5 and c != 1:
                extras.append((r, c))
    
    # Sort by row, then col
    extras.sort()
    
    # Compute deltas
    p1, p2 = extras
    delta_r = p2[0] - p1[0]
    delta_c = p2[1] - p1[1]
    
    # Determine color
    if delta_r == 0:
        color = 1
    elif delta_r * delta_c > 0:
        color = 2
    else:
        color = 3
    
    # Create output: replace 5 in right with color, 0 remains 0
    out = np.zeros((3, 3), dtype=int)
    out[right == 5] = color
    
    return out.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
