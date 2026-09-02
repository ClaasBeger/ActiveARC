"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: fc754716
source: GitMonsters/SOLVED-562-verified
original_path: solves/fc754716/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__fc754716
"""
from __future__ import annotations



def solve(grid):
    rows = len(grid)
    cols = len(grid[0])
    color = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                color = grid[r][c]
                break
        if color:
            break
    result = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if r == 0 or r == rows - 1 or c == 0 or c == cols - 1:
                result[r][c] = color
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
