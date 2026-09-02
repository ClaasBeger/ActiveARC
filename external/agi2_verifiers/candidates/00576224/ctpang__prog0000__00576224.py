"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 00576224
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[0](id=0)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0000__00576224
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    A = grid[0][0]
    B = grid[0][1]
    C = grid[1][0]
    D = grid[1][1]
    
    normal1 = [A, B] * 3
    normal2 = [C, D] * 3
    rev1 = [B, A] * 3
    rev2 = [D, C] * 3
    
    output = [
        normal1,
        normal2,
        rev1,
        rev2,
        normal1,
        normal2
    ]
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
