"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 59341089
source: GitMonsters/SOLVED-562-verified
original_path: solves/59341089/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__59341089
"""
from __future__ import annotations



def solve(grid):
    """Reverse each row, concat with original, tile 2x horizontally."""
    R = len(grid)
    half = []
    for r in range(R):
        half.append(grid[r][::-1] + grid[r])
    # Tile the 3x6 half twice to get 3x12
    return [row * 2 for row in half]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
