"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: d492a647
source: GitMonsters/SOLVED-562-verified
original_path: solves/d492a647/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__d492a647
"""
from __future__ import annotations



import json
from typing import List

def solve(grid: List[List[int]]) -> List[List[int]]:
    """
    ARC-AGI puzzle d492a647 solver.
    
    Pattern: Find the special marker (any value not 0 or 5).
    Replace all 0s that have the same row and column parity as the marker
    with the marker color.
    """
    # Create output grid as a copy of input
    result = [row[:] for row in grid]
    
    # Find the special marker (not 0 or 5)
    marker = None
    marker_r = None
    marker_c = None
    
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val not in [0, 5]:
                marker = val
                marker_r = r
                marker_c = c
                break
        if marker is not None:
            break
    
    # If no marker found, return grid as is
    if marker is None:
        return result
    
    # Get marker parities
    marker_row_parity = marker_r % 2
    marker_col_parity = marker_c % 2
    
    # Replace 0s with matching parity with the marker color
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val == 0:
                row_parity = r % 2
                col_parity = c % 2
                
                if row_parity == marker_row_parity and col_parity == marker_col_parity:
                    result[r][c] = marker
    
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
