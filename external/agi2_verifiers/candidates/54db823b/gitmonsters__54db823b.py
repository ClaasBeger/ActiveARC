"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 54db823b
source: GitMonsters/SOLVED-562-verified
original_path: solves/54db823b/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__54db823b
"""
from __future__ import annotations



"""
Solver for ARC-AGI task 54db823b

Rule: Find all connected components (blocks) that contain both 3 and 9.
Among these mixed blocks, identify the one with the lowest count of 9s.
Remove (set to 0) all cells in that block.
"""

import json
from scipy import ndimage
import numpy as np


def solve(grid):
    """
    Solve ARC task 54db823b.
    
    Args:
        grid: List of lists representing the input grid
        
    Returns:
        List of lists representing the output grid
    """
    arr = np.array(grid, dtype=int)
    nonzero = arr > 0
    labeled, num_features = ndimage.label(nonzero)
    
    # Find all blocks with both 3 and 9, and their 9-counts
    mixed_blocks = []
    
    for label in range(1, num_features + 1):
        coords = np.where(labeled == label)
        if len(coords[0]) > 0:
            vals = arr[labeled == label]
            
            if 3 in vals and 9 in vals:
                count_9 = int((vals == 9).sum())
                mixed_blocks.append((label, count_9))
    
    # Clear the block with the lowest count of 9s
    result = arr.copy()
    if mixed_blocks:
        target_label = min(mixed_blocks, key=lambda x: x[1])[0]
        result[labeled == target_label] = 0
    
    return result.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
