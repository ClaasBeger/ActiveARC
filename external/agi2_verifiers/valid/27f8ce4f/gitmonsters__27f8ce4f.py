"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 27f8ce4f
source: GitMonsters/SOLVED-562-verified
original_path: solves/27f8ce4f/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__27f8ce4f
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """Find most common color. Place input copies at positions matching that color in the 3x3 grid."""
    from collections import Counter
    n = len(grid)
    counts: Counter = Counter()
    for r in range(n):
        for c in range(n):
            counts[grid[r][c]] += 1
    most_common = counts.most_common(1)[0][0]

    out = [[0]*(n*n) for _ in range(n*n)]
    for br in range(n):
        for bc in range(n):
            if grid[br][bc] == most_common:
                for r in range(n):
                    for c in range(n):
                        out[br*n + r][bc*n + c] = grid[r][c]

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
