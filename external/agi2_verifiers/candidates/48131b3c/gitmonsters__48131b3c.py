"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 48131b3c
source: GitMonsters/SOLVED-562-verified
original_path: solves/48131b3c/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__48131b3c
"""
from __future__ import annotations



def solve(grid):
    """Invert (swap 0 and non-zero color) then tile 2x2."""
    R, C = len(grid), len(grid[0])
    # Find the non-zero color
    color = 0
    for row in grid:
        for v in row:
            if v != 0:
                color = v
                break
        if color:
            break
    # Create inverted grid
    inv = [[color if v == 0 else 0 for v in row] for row in grid]
    # Tile 2x2
    out = []
    for br in range(2):
        for r in range(R):
            row = []
            for bc in range(2):
                row.extend(inv[r])
            out.append(row)
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
