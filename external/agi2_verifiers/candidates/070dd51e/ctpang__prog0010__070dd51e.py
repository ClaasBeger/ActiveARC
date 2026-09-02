"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 070dd51e
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[10](id=10)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0010__070dd51e
"""
from __future__ import annotations



import numpy as np

from collections import defaultdict

def transform(grid: list[list[int]]) -> list[list[int]]:
    height = len(grid)
    width = len(grid[0])
    output = [[0 for _ in range(width)] for _ in range(height)]
    
    pos = defaultdict(list)
    for r in range(height):
        for c in range(width):
            color = grid[r][c]
            if color > 0:
                pos[color].append((r, c))
    
    horizontals = []
    verticals = []
    for color, positions in pos.items():
        if len(positions) == 2:
            (r1, c1), (r2, c2) = positions
            if r1 == r2:
                min_c = min(c1, c2)
                max_c = max(c1, c2)
                horizontals.append((r1, min_c, max_c, color))
            elif c1 == c2:
                min_r = min(r1, r2)
                max_r = max(r1, r2)
                verticals.append((c1, min_r, max_r, color))
    
    # Fill horizontals first
    for row, min_c, max_c, color in horizontals:
        for c in range(min_c, max_c + 1):
            output[row][c] = color
    
    # Then fill verticals, overwriting
    for col, min_r, max_r, color in verticals:
        for r in range(min_r, max_r + 1):
            output[r][col] = color
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
