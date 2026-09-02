"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 3979b1a8
source: GitMonsters/SOLVED-562-verified
original_path: solves/3979b1a8/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__3979b1a8
"""
from __future__ import annotations



"""
Solver for ARC task 3979b1a8.

The input is a 5x5 symmetric grid with 3 concentric ring colors (corner, edge, center).
The output is 10x10: the original grid in the top-left, extended with L-shaped bands
that cycle through [corner, center, edge]. Each band's corner cell uses the next color
in the cycle.
"""

import json
from typing import List


def solve(grid: List[List[int]]) -> List[List[int]]:
    N = len(grid)
    # Extract the 3 concentric ring colors from the diagonal
    c0 = grid[0][0]        # corner
    c1 = grid[1][1]        # edge
    c2 = grid[N // 2][N // 2]  # center
    cycle = [c0, c2, c1]   # arm color cycle

    size = 2 * N
    out = [[0] * size for _ in range(size)]

    for r in range(size):
        for c in range(size):
            if r < N and c < N:
                out[r][c] = grid[r][c]
            else:
                d = max(r, c)
                band_idx = d - N
                if r == c:
                    out[r][c] = cycle[(band_idx + 1) % 3]
                else:
                    out[r][c] = cycle[band_idx % 3]
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
