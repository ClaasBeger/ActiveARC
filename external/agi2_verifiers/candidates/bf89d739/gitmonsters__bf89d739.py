"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: bf89d739
source: GitMonsters/SOLVED-562-verified
original_path: solves/bf89d739/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__bf89d739
"""
from __future__ import annotations



import json

def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    Connect all 2s using a Steiner tree with either horizontal or vertical spine.
    Choose the spine orientation based on which creates a shorter total path.
    """
    result = [row[:] for row in grid]
    
    # Find all 2s
    twos = []
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 2:
                twos.append((r, c))
    
    if len(twos) < 2:
        return result
    
    rows = sorted([r for r, c in twos])
    cols = sorted([c for r, c in twos])
    unique_rows = len(set(rows))
    unique_cols = len(set(cols))
    
    if unique_rows <= unique_cols:
        # Use horizontal spine at median row
        median_row = rows[len(rows) // 2]
        min_col, max_col = cols[0], cols[-1]
        
        # Draw horizontal spine at median row
        for c in range(min_col, max_col + 1):
            if result[median_row][c] == 0:
                result[median_row][c] = 3
        
        # Branch from spine to each 2
        for r, c in twos:
            # Connect vertically from 2 to spine
            start_r, end_r = min(r, median_row), max(r, median_row)
            for row in range(start_r + 1, end_r):
                if result[row][c] == 0:
                    result[row][c] = 3
    else:
        # Use vertical spine at median column
        median_col = cols[len(cols) // 2]
        min_row, max_row = rows[0], rows[-1]
        
        # Draw vertical spine at median column
        for r in range(min_row, max_row + 1):
            if result[r][median_col] == 0:
                result[r][median_col] = 3
        
        # Branch from spine to each 2
        for r, c in twos:
            # Connect horizontally from 2 to spine
            start_c, end_c = min(c, median_col), max(c, median_col)
            for col in range(start_c + 1, end_c):
                if result[r][col] == 0:
                    result[r][col] = 3
    
    # Keep the 2s as 2
    for r, c in twos:
        result[r][c] = 2
    
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
