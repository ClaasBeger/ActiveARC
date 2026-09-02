"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: bf89d739
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[405](id=405)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0405__bf89d739
"""
from __future__ import annotations



import numpy as np

import copy

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    rows = len(grid)
    cols = len(grid[0])
    reds = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                reds.append((r, c))
    
    if not reds:
        return grid
    
    red_rs = [r for r, c in reds]
    red_cs = [c for r, c in reds]
    
    unique_rows = len(set(red_rs))
    unique_cols = len(set(red_cs))
    
    median_r = sorted(red_rs)[len(red_rs) // 2]
    median_c = sorted(red_cs)[len(red_cs) // 2]
    
    min_r = min(red_rs)
    max_r = max(red_rs)
    min_c = min(red_cs)
    max_c = max(red_cs)
    
    output = [row[:] for row in grid]
    
    if unique_rows > unique_cols:
        # Main vertical at median_c from min_r to max_r
        for rr in range(min_r, max_r + 1):
            if output[rr][median_c] == 0:
                output[rr][median_c] = 3
        
        # Connect horizontally for off-main seeds
        for r, c in reds:
            if c != median_c:
                start_c = min(c, median_c)
                end_c = max(c, median_c)
                for cc in range(start_c, end_c + 1):
                    if output[r][cc] == 0:
                        output[r][cc] = 3
    else:
        # Main horizontal at median_r from min_c to max_c
        for cc in range(min_c, max_c + 1):
            if output[median_r][cc] == 0:
                output[median_r][cc] = 3
        
        # Connect vertically for off-main seeds
        for r, c in reds:
            if r != median_r:
                start_r = min(r, median_r)
                end_r = max(r, median_r)
                for rr in range(start_r, end_r + 1):
                    if output[rr][c] == 0:
                        output[rr][c] = 3
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
