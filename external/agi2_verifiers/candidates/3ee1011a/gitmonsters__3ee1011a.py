"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 3ee1011a
source: GitMonsters/SOLVED-562-verified
original_path: solves/3ee1011a/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__3ee1011a
"""
from __future__ import annotations



#!/usr/bin/env python3
import json
import sys
from typing import List


def solve(grid: List[List[int]]) -> List[List[int]]:
    """
    Solution for ARC-AGI task 3ee1011a.
    
    The transformation creates concentric rectangular frames in an NxN grid,
    where N is the count of the most frequent non-zero color.
    Each non-zero color creates one frame layer, ordered by count (descending).
    """
    # Count occurrences of each non-zero color
    color_counts = {}
    for row in grid:
        for val in row:
            if val != 0:
                color_counts[val] = color_counts.get(val, 0) + 1
    
    if not color_counts:
        return [[]]
    
    # Sort colors by count (descending)
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Output size is the max count
    n = sorted_colors[0][1]
    
    # Create output grid filled with the outermost color
    output = [[0] * n for _ in range(n)]
    
    # Fill concentric frames from outside to inside
    for layer_idx, (color, count) in enumerate(sorted_colors):
        # layer_idx tells us which frame we're drawing (0 = outermost)
        for i in range(layer_idx, n - layer_idx):
            for j in range(layer_idx, n - layer_idx):
                # Only fill the border of this layer
                if i == layer_idx or i == n - 1 - layer_idx or j == layer_idx or j == n - 1 - layer_idx:
                    output[i][j] = color
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
