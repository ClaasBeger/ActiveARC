"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e633a9e5
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[487](id=487)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0487__e633a9e5
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    # Expand each row horizontally
    expanded_rows = []
    for row in grid:
        a, b, c = row
        expanded = [a, a, b, c, c]
        expanded_rows.append(expanded)
    
    # Create output by duplicating rows vertically
    output = []
    output.append(expanded_rows[0])
    output.append(expanded_rows[0])
    output.append(expanded_rows[1])
    output.append(expanded_rows[2])
    output.append(expanded_rows[2])
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
