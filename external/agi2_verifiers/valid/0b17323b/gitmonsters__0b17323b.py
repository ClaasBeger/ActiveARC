"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 0b17323b
source: GitMonsters/SOLVED-562-verified
original_path: solves/0b17323b/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__0b17323b
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    result = [row[:] for row in grid]
    
    # Find all blue (1) dots
    ones = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                ones.append((r, c))
    
    # Sort by row then col
    ones.sort()
    
    # Compute step from first two points
    dr = ones[1][0] - ones[0][0]
    dc = ones[1][1] - ones[0][1]
    
    # Continue from last blue dot
    last_r, last_c = ones[-1]
    r, c = last_r + dr, last_c + dc
    while 0 <= r < rows and 0 <= c < cols:
        result[r][c] = 2
        r += dr
        c += dc
    
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
