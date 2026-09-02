"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: bc4146bd
source: GitMonsters/SOLVED-562-verified
original_path: solves/bc4146bd/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__bc4146bd
"""
from __future__ import annotations



def solve(grid):
    """Tile 5 times horizontally, alternating original and reversed rows."""
    rows = len(grid)
    result = []
    for r in range(rows):
        original = grid[r]
        reversed_row = original[::-1]
        out_row = []
        for t in range(5):
            if t % 2 == 0:
                out_row.extend(original)
            else:
                out_row.extend(reversed_row)
        result.append(out_row)
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
