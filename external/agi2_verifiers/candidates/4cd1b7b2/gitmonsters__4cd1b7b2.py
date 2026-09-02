"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 4cd1b7b2
source: GitMonsters/SOLVED-562-verified
original_path: solves/4cd1b7b2/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__4cd1b7b2
"""
from __future__ import annotations



def solve(grid):
    """Complete a 4x4 Latin square: fill 0s so each row/col has {1,2,3,4}."""
    g = [row[:] for row in grid]
    full = {1, 2, 3, 4}

    def backtrack():
        for r in range(4):
            for c in range(4):
                if g[r][c] == 0:
                    row_vals = {g[r][cc] for cc in range(4) if g[r][cc] != 0}
                    col_vals = {g[rr][c] for rr in range(4) if g[rr][c] != 0}
                    for v in full - row_vals - col_vals:
                        g[r][c] = v
                        if backtrack():
                            return True
                        g[r][c] = 0
                    return False
        return True

    backtrack()
    return g

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
