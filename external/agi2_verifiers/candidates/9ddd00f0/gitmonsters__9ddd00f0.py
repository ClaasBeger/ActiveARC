"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9ddd00f0
source: GitMonsters/SOLVED-562-verified
original_path: solves/9ddd00f0/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__9ddd00f0
"""
from __future__ import annotations



def solve(grid):
    """Grid is NxN where N = K²+K-1. Divided into KxK blocks of size KxK.
    Each block position (br,bc) gets filled with 'color' except a hole at (br,bc)."""
    n = len(grid)

    # Find K: n = K*(K+1) - 1
    k = None
    for candidate in range(1, n + 1):
        if candidate * (candidate + 1) - 1 == n:
            k = candidate
            break

    # Find the non-zero color
    color = 0
    for r in range(n):
        for c in range(n):
            if grid[r][c] != 0:
                color = grid[r][c]
                break
        if color != 0:
            break

    # Build output
    result = [[0] * n for _ in range(n)]
    for br in range(k):
        for bc in range(k):
            rs = br * (k + 1)
            cs = bc * (k + 1)
            for lr in range(k):
                for lc in range(k):
                    if lr == br and lc == bc:
                        result[rs + lr][cs + lc] = 0
                    else:
                        result[rs + lr][cs + lc] = color
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
