"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 6d1d5c90
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[231](id=231)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0231__6d1d5c90
"""
from __future__ import annotations



import numpy as np

from collections import Counter

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    
    n = len(grid)
    m = len(grid[0])
    
    left_col = [row[0] for row in grid]
    counts = Counter(left_col)
    majority = counts.most_common(1)[0][0]
    
    r = None
    for i in range(n):
        if grid[i][0] != majority:
            r = i
            break
    
    if r is None:
        r = 0  # Default if no marker, though examples always have one
    
    new_grid = []
    for i in range(n):
        old_row_idx = (i - r + n) % n
        new_row = grid[old_row_idx][1:]
        new_grid.append(new_row)
    
    return new_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
