"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: d37a1ef5
source: GitMonsters/SOLVED-562-verified
original_path: solves/d37a1ef5/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__d37a1ef5
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    Fill the interior of a 2-colored rectangle with 2s, except for the region
    defined by the bounding box of any 5s in the grid.
    
    The rule: 
    1. Find the rectangular region bounded by 2s
    2. Find the bounding box of all 5s in the grid
    3. Fill all 0s inside the 2-rectangle with 2s, EXCEPT those within the 5s bounding box
    """
    result = [row[:] for row in grid]
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    # Find the bounding box of the rectangle made of 2s
    min_r_2, max_r_2 = rows, -1
    min_c_2, max_c_2 = cols, -1
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                min_r_2 = min(min_r_2, r)
                max_r_2 = max(max_r_2, r)
                min_c_2 = min(min_c_2, c)
                max_c_2 = max(max_c_2, c)
    
    if min_r_2 > max_r_2 or min_c_2 > max_c_2:
        return result
    
    # Find the bounding box of all 5s
    min_r_5, max_r_5 = rows, -1
    min_c_5, max_c_5 = cols, -1
    has_fives = False
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 5:
                has_fives = True
                min_r_5 = min(min_r_5, r)
                max_r_5 = max(max_r_5, r)
                min_c_5 = min(min_c_5, c)
                max_c_5 = max(max_c_5, c)
    
    # Fill interior of the 2-rectangle, except the 5s region
    for r in range(min_r_2 + 1, max_r_2):
        for c in range(min_c_2 + 1, max_c_2):
            if result[r][c] == 0:
                # Don't fill if this cell is within the 5s bounding box
                if has_fives and min_r_5 <= r <= max_r_5 and min_c_5 <= c <= max_c_5:
                    continue
                result[r][c] = 2
    
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
