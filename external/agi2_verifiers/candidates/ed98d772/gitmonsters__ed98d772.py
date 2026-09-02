"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ed98d772
source: GitMonsters/SOLVED-562-verified
original_path: solves/ed98d772/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__ed98d772
"""
from __future__ import annotations



def solve(grid):
    n = len(grid)
    m = len(grid[0])

    def rot90cw(g):
        """Rotate 90 degrees clockwise."""
        r = len(g)
        c = len(g[0])
        return [[g[r - 1 - j][i] for j in range(r)] for i in range(c)]

    def rot90ccw(g):
        """Rotate 90 degrees counter-clockwise."""
        r = len(g)
        c = len(g[0])
        return [[g[j][c - 1 - i] for j in range(r)] for i in range(c)]

    def rot180(g):
        """Rotate 180 degrees."""
        r = len(g)
        c = len(g[0])
        return [[g[r - 1 - i][c - 1 - j] for j in range(c)] for i in range(r)]

    identity = grid
    top_right = rot90ccw(grid)
    bottom_left = rot180(grid)
    bottom_right = rot90cw(grid)

    out = []
    # Top half
    for r in range(n):
        out.append(identity[r] + top_right[r])
    # Bottom half
    for r in range(n):
        out.append(bottom_left[r] + bottom_right[r])
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
