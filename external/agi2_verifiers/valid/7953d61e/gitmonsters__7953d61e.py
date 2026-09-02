"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 7953d61e
source: GitMonsters/SOLVED-562-verified
original_path: solves/7953d61e/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__7953d61e
"""
from __future__ import annotations



def solve(grid):
    """Tile input in 2x2: TL=id, TR=rot90CCW, BL=rot180, BR=rot270CCW."""
    n = len(grid)
    m = len(grid[0])

    def rot90ccw(g):
        # new[i][j] = g[j][n-1-i] where n=rows of g
        r, c = len(g), len(g[0])
        return [[g[j][r - 1 - i] for j in range(c)] for i in range(r)]

    def rot180(g):
        r, c = len(g), len(g[0])
        return [[g[r - 1 - i][c - 1 - j] for j in range(c)] for i in range(r)]

    def rot270ccw(g):
        # = rot90CW: new[i][j] = g[n-1-j][i]
        r, c = len(g), len(g[0])
        return [[g[c - 1 - j][i] for j in range(c)] for i in range(r)]

    tl = [row[:] for row in grid]
    tr = rot90ccw(grid)
    bl = rot180(grid)
    br = rot270ccw(grid)

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
