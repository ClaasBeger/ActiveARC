"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 4f537728
source: GitMonsters/SOLVED-562-verified
original_path: solves/4f537728/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__4f537728
"""
from __future__ import annotations



import json
import sys


def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    Find the special color (non-0, non-1 value) in the grid.
    Paint the entire column(s) and row(s) containing that color with it.
    """
    # Create output as a copy
    output = [row[:] for row in grid]
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    
    # Find all non-zero, non-one values (the special color)
    special_color = None
    special_positions = []
    
    for r in range(height):
        for c in range(width):
            val = grid[r][c]
            if val not in (0, 1):
                if special_color is None:
                    special_color = val
                special_positions.append((r, c))
    
    if special_color is None:
        return output
    
    # Find which rows and columns contain the special color
    special_rows = set(r for r, c in special_positions)
    special_cols = set(c for r, c in special_positions)
    
    # Paint entire columns and rows with the special color
    for r in range(height):
        for c in range(width):
            # Skip rows and columns that are all zeros
            if grid[r][c] != 0:
                if r in special_rows or c in special_cols:
                    output[r][c] = special_color
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
