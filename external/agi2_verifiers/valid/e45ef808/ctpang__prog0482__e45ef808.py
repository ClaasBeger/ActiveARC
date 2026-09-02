"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e45ef808
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[482](id=482)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0482__e45ef808
"""
from __future__ import annotations



import numpy as np

import copy

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    
    h = len(grid)
    w = len(grid[0])
    output = copy.deepcopy(grid)
    
    # Compute top_r for each column
    top_r = [h] * w  # Initialize to h (beyond grid) in case no 6
    for c in range(w):
        for r in range(h):
            if grid[r][c] == 6:
                top_r[c] = r
                break
    
    # Find minimal top_r (tallest peak), rightmost if tie
    min_top = min(top_r)
    peak_col = max(c for c in range(w) if top_r[c] == min_top)
    
    # Find maximal top_r (deepest valley), leftmost if tie
    max_top = max(top_r)
    valley_col = min(c for c in range(w) if top_r[c] == max_top)
    
    # Extend peak with yellow (4) from row 1 to top_r[peak_col]-1
    for r in range(1, top_r[peak_col]):
        output[r][peak_col] = 4
    
    # Extend valley with brown (9) from row 1 to top_r[valley_col]-1
    for r in range(1, top_r[valley_col]):
        output[r][valley_col] = 9
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
