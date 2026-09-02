"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e9bb6954
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[505](id=505)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0505__e9bb6954
"""
from __future__ import annotations



import numpy as np

from collections import defaultdict
import copy

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    height = len(grid)
    width = len(grid[0])
    claims = defaultdict(list)
    
    # Find all 3x3 monochromatic squares
    for r in range(height - 2):
        for c in range(width - 2):
            # Collect the 9 cells
            cells = [grid[r + i][c + j] for i in range(3) for j in range(3)]
            unique_colors = set(cells)
            if len(unique_colors) == 1:
                color = list(unique_colors)[0]
                if color > 0:
                    r_center = r + 1
                    c_center = c + 1
                    # Claim horizontal line
                    for k in range(width):
                        claims[(r_center, k)].append(color)
                    # Claim vertical line
                    for k in range(height):
                        claims[(k, c_center)].append(color)
    
    # Create output as copy of input
    output = copy.deepcopy(grid)
    
    # Resolve claims
    for (r, c), ls in claims.items():
        s = set(ls)
        if len(s) == 1:
            output[r][c] = list(s)[0]
        elif len(s) > 1:
            output[r][c] = 0
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
