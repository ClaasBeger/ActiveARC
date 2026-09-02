"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 34b99a2b
source: GitMonsters/SOLVED-562-verified
original_path: solves/34b99a2b/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__34b99a2b
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """XOR left and right halves separated by column of 4s. Output 2 where exactly one is non-zero."""
    rows = len(grid)
    cols = len(grid[0])

    div = next(c for c in range(cols) if all(grid[r][c] == 4 for r in range(rows)))
    w = div

    out = []
    for r in range(rows):
        row = []
        for c in range(w):
            left = grid[r][c] != 0
            right = grid[r][div + 1 + c] != 0
            row.append(2 if left != right else 0)
        out.append(row)
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
