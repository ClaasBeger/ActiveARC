"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 0c9aba6e
source: GitMonsters/SOLVED-562-verified
original_path: solves/0c9aba6e/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__0c9aba6e
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    # Find the separator row (all 7s)
    sep = next(i for i, row in enumerate(grid) if all(c == 7 for c in row))
    top = grid[:sep]
    bottom = grid[sep + 1:]
    # NOR: output 8 where both halves are 0, else 0
    return [
        [8 if top[r][c] == 0 and bottom[r][c] == 0 else 0
         for c in range(len(top[0]))]
        for r in range(len(top))
    ]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
