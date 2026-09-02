"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 6f473927
source: GitMonsters/SOLVED-562-verified
original_path: solves/6f473927/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__6f473927
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    Rule: Double the width based on first element of first row
    If grid[0][0] == 0:
      - Left: original, Right: flip + invert
    If grid[0][0] == 2:
      - Left: flip + invert, Right: original
    """
    if not grid or not grid[0]:
        return grid
    
    use_flip_left = grid[0][0] == 2
    result = []
    
    for row in grid:
        flipped = row[::-1]
        inverted = [8 if cell == 0 else 0 for cell in flipped]
        
        if use_flip_left:
            # flip+invert on left, original on right
            new_row = inverted + row
        else:
            # original on left, flip+invert on right
            new_row = row + inverted
        
        result.append(new_row)
    
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
