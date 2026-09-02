"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 0c786b71
source: GitMonsters/SOLVED-562-verified
original_path: solves/0c786b71/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__0c786b71
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """2x2 arrangement: top-left=rot180, top-right=flip_ud, bottom-left=flip_lr, bottom-right=identity."""
    r = len(grid)
    c = len(grid[0])

    rot180 = [row[::-1] for row in grid[::-1]]
    flip_ud = grid[::-1]
    flip_lr = [row[::-1] for row in grid]
    identity = grid

    out = []
    for i in range(r):
        out.append(rot180[i] + flip_ud[i])
    for i in range(r):
        out.append(flip_lr[i] + identity[i])
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
