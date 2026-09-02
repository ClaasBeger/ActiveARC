"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 59341089
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[189](id=189)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0189__59341089
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    if rows == 0:
        return []
    cols = len(grid[0])
    
    # Create horizontal flip
    flip = [row[::-1] for row in grid]
    
    # Parts to concatenate: flip, original, flip, original
    parts = [flip, grid, flip, grid]
    
    # Build output
    out = []
    for r in range(rows):
        out_row = []
        for part in parts:
            out_row.extend(part[r])
        out.append(out_row)
    
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
