"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: a59b95c0
source: GitMonsters/SOLVED-562-verified
original_path: solves/a59b95c0/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__a59b95c0
"""
from __future__ import annotations



def solve(grid):
    """Tile the 3x3 input NxN times where N = number of distinct colors."""
    colors = set()
    for row in grid:
        for cell in row:
            colors.add(cell)
    n = len(colors)
    rows = len(grid)
    cols = len(grid[0])
    result = []
    for r in range(rows * n):
        result.append([grid[r % rows][c % cols] for c in range(cols * n)])
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
