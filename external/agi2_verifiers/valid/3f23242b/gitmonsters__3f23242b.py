"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 3f23242b
source: GitMonsters/SOLVED-562-verified
original_path: solves/3f23242b/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__3f23242b
"""
from __future__ import annotations



import json
import sys


def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    For each cell with value 3, draw a cross pattern:
    - Horizontal line at r+2: filled with 8s (center area), surrounded by 2s extending to edges
    - Vertical line at c: filled with pattern above
    - Top area (r-2): 5s in center
    - Sides: 2s forming box outline
    """
    # Create a copy of the input grid
    height = len(grid)
    width = len(grid[0])
    output = [row[:] for row in grid]
    
    # Find all 3s in the input
    threes = []
    for r in range(height):
        for c in range(width):
            if grid[r][c] == 3:
                threes.append((r, c))
    
    # For each 3, draw the pattern
    for r, c in threes:
        # Draw the cross pattern around the 3
        
        # Top row (r-2): 5s
        if r - 2 >= 0:
            for cc in range(max(0, c - 2), min(width, c + 3)):
                output[r - 2][cc] = 5
        
        # Second row (r-1): 2s on sides with 5 in middle
        if r - 1 >= 0:
            if c - 2 >= 0:
                output[r - 1][c - 2] = 2
            if c >= 0 and c < width:
                output[r - 1][c] = 5
            if c + 2 < width:
                output[r - 1][c + 2] = 2
        
        # Third row (r): the 3 stays, add 2s on sides
        if r >= 0 and r < height:
            if c - 2 >= 0:
                output[r][c - 2] = 2
            # 3 is already there
            if c + 2 < width:
                output[r][c + 2] = 2
        
        # Fourth row (r+1): 2s on sides
        if r + 1 < height:
            if c - 2 >= 0:
                output[r + 1][c - 2] = 2
            if c + 2 < width:
                output[r + 1][c + 2] = 2
        
        # Fifth row (r+2): horizontal line with 8s in center and 2s extending outward
        if r + 2 < height:
            # Fill entire row with 2s first
            for cc in range(width):
                output[r + 2][cc] = 2
            # Then fill center area with 8s
            for cc in range(max(0, c - 2), min(width, c + 3)):
                output[r + 2][cc] = 8
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
