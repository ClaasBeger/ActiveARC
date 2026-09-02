"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 0f63c0b9
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[21](id=21)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0021__0f63c0b9
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    height = len(grid)
    width = len(grid[0])
    output = [[0] * width for _ in range(height)]
    
    # Collect seeds: (row, col, color)
    seeds = []
    for r in range(height):
        for c in range(width):
            if grid[r][c] != 0:
                seeds.append((r, c, grid[r][c]))
    
    # Sort by row
    seeds.sort(key=lambda x: x[0])
    n = len(seeds)
    if n == 0:
        return output
    
    # Compute ends
    ends = []
    for i in range(n - 1):
        ri = seeds[i][0]
        rj = seeds[i + 1][0]
        end = (ri + rj) // 2
        ends.append(end)
    ends.append(height - 1)
    
    # Compute starts
    starts = [0]
    for i in range(n - 1):
        next_start = ends[i] + 1
        starts.append(next_start)
    
    # For each bar
    for k in range(n):
        start_r = starts[k]
        end_r = ends[k]
        color = seeds[k][2]
        seed_r = seeds[k][0]
        
        # Set sides
        for r in range(start_r, end_r + 1):
            output[r][0] = color
            output[r][width - 1] = color
        
        # Set full at seed_r
        for c in range(width):
            output[seed_r][c] = color
        
        # If touches top
        if start_r == 0:
            for c in range(width):
                output[0][c] = color
        
        # If touches bottom
        if end_r == height - 1:
            for c in range(width):
                output[height - 1][c] = color
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
