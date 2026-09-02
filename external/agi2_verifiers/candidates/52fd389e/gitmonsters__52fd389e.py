"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 52fd389e
source: GitMonsters/SOLVED-562-verified
original_path: solves/52fd389e/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__52fd389e
"""
from __future__ import annotations



import json
import numpy as np
from scipy import ndimage


def solve(grid):
    """
    For each connected region of 4s:
    1. Find marking color (non-zero, non-4 cell in region)
    2. Count number of marked cells
    3. Expand region by count cells in all directions
    4. Fill expanded border with marking color
    """
    grid = np.array(grid)
    output = grid.copy().astype(int)
    h, w = grid.shape
    
    # Find connected components of 4s
    labeled, num_features = ndimage.label(grid == 4)
    
    for region_id in range(1, num_features + 1):
        region_mask = labeled == region_id
        fours_pos = np.where(region_mask)
        
        r_min, r_max = fours_pos[0].min(), fours_pos[0].max()
        c_min, c_max = fours_pos[1].min(), fours_pos[1].max()
        
        # Find marking color and count marked cells
        region = grid[r_min:r_max+1, c_min:c_max+1]
        marks = region[(region != 0) & (region != 4)]
        
        if len(marks) == 0:
            continue
        
        marking_color = int(marks[0])
        mark_count = len(marks)
        
        # Expand by mark_count cells in all directions
        border_r_min = max(0, r_min - mark_count)
        border_r_max = min(h - 1, r_max + mark_count)
        border_c_min = max(0, c_min - mark_count)
        border_c_max = min(w - 1, c_max + mark_count)
        
        # Fill border with marking color (except where 4s are)
        for r in range(border_r_min, border_r_max + 1):
            for c in range(border_c_min, border_c_max + 1):
                if grid[r, c] != 4:
                    output[r, c] = marking_color
    
    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
