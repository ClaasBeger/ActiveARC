"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 0692e18c
source: GitMonsters/SOLVED-562-verified
original_path: solves/0692e18c/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__0692e18c
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """Each non-zero cell maps to a 3x3 block that is the inverted pattern of the input."""
    n = len(grid)
    color = 0
    for r in range(n):
        for c in range(n):
            if grid[r][c] != 0:
                color = grid[r][c]
                break
        if color:
            break

    inverted = [[0]*n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            inverted[r][c] = 0 if grid[r][c] != 0 else color

    out_size = n * n
    out = [[0]*out_size for _ in range(out_size)]

    for br in range(n):
        for bc in range(n):
            if grid[br][bc] != 0:
                for r in range(n):
                    for c in range(n):
                        out[br*n + r][bc*n + c] = inverted[r][c]

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
