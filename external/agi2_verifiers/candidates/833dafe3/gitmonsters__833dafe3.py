"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 833dafe3
source: GitMonsters/SOLVED-562-verified
original_path: solves/833dafe3/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__833dafe3
"""
from __future__ import annotations



def solve(grid):
    """Tile input 2x2: TL=rot180, TR=flipud, BL=fliplr, BR=identity."""
    n = len(grid)
    m = len(grid[0])

    def rot180(g):
        return [[g[len(g) - 1 - i][len(g[0]) - 1 - j] for j in range(len(g[0]))] for i in range(len(g))]

    def flipud(g):
        return [row[:] for row in reversed(g)]

    def fliplr(g):
        return [row[::-1] for row in g]

    tl = rot180(grid)
    tr = flipud(grid)
    bl = fliplr(grid)
    br = [row[:] for row in grid]

    out = []
    for i in range(n):
        out.append(tl[i] + tr[i])
    for i in range(n):
        out.append(bl[i] + br[i])
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
