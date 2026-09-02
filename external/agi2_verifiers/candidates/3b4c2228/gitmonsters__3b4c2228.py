"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 3b4c2228
source: GitMonsters/SOLVED-562-verified
original_path: solves/3b4c2228/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__3b4c2228
"""
from __future__ import annotations



#!/usr/bin/env python3
"""
Solver for ARC-AGI task 3b4c2228.

Rule: Count 2x2 blocks of value 3 in the input grid.
Create a 3x3 output grid with 1s on the main diagonal,
with the number of 1s equal to the count of 2x2 blocks of 3.
"""

def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    Solve ARC task 3b4c2228.
    
    Args:
        grid: Input grid as list of lists of integers
        
    Returns:
        3x3 output grid with 1s on diagonal
    """
    # Count 2x2 blocks of value 3
    block_count = 0
    h = len(grid)
    w = len(grid[0]) if h > 0 else 0
    
    for r in range(h - 1):
        for c in range(w - 1):
            if (grid[r][c] == 3 and grid[r][c + 1] == 3 and
                grid[r + 1][c] == 3 and grid[r + 1][c + 1] == 3):
                block_count += 1
    
    # Create 3x3 output with 1s on diagonal based on block_count
    output = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for i in range(min(block_count, 3)):
        output[i][i] = 1
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
