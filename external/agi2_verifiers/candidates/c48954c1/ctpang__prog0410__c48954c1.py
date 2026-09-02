"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: c48954c1
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[410](id=410)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0410__c48954c1
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if len(grid) != 3 or any(len(row) != 3 for row in grid):
        raise ValueError("Input must be 3x3 grid")
    
    row_indices = [2, 1, 0, 0, 1, 2, 2, 1, 0]
    output = []
    
    for i in range(9):
        idx = row_indices[i]
        middle = grid[idx][:]
        left = middle[::-1]
        right = left[:]
        output_row = left + middle + right
        output.append(output_row)
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
