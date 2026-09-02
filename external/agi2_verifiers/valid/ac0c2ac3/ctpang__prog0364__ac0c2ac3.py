"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ac0c2ac3
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[364](id=364)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0364__ac0c2ac3
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    height = len(grid)
    width = len(grid[0])
    background = 7  # Based on examples
    
    # Map from k to color
    k_to_color = {}
    
    for r in range(height):
        for c in range(width):
            if grid[r][c] != background:
                k = min(r, height - 1 - r, c, width - 1 - c)
                k_to_color[k] = grid[r][c]
    
    # Create output
    output = [[0 for _ in range(width)] for _ in range(height)]
    
    for r in range(height):
        for c in range(width):
            k = min(r, height - 1 - r, c, width - 1 - c)
            output[r][c] = k_to_color[k]
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
