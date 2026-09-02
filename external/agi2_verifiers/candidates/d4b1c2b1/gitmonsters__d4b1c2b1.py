"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: d4b1c2b1
source: GitMonsters/SOLVED-562-verified
original_path: solves/d4b1c2b1/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__d4b1c2b1
"""
from __future__ import annotations



def solve(grid):
    distinct = len(set(v for row in grid for v in row))
    scale = distinct
    rows = len(grid)
    cols = len(grid[0])
    out = []
    for r in range(rows):
        for _ in range(scale):
            row = []
            for c in range(cols):
                row.extend([grid[r][c]] * scale)
            out.append(row)
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
