"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 695367ec
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[223](id=223)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0223__695367ec
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    n = len(grid)
    c = grid[0][0]  # Assuming all cells are c
    
    # Build sparse row
    unit_len = n + 1
    unit = [0] * n + [c]
    num_full_units = 15 // unit_len
    remainder = 15 % unit_len
    sparse_row = []
    for _ in range(num_full_units):
        sparse_row.extend(unit)
    sparse_row.extend([0] * remainder)
    
    # Build output rows
    period = n + 1
    num_full_periods = 15 // period
    rem_rows = 15 % period
    output = []
    for _ in range(num_full_periods):
        for _ in range(n):
            output.append(sparse_row[:])
        output.append([c] * 15)
    for _ in range(rem_rows):
        output.append(sparse_row[:])
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
