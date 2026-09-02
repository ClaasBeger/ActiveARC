"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 60c09cac
source: GitMonsters/SOLVED-562-verified
original_path: solves/60c09cac/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__60c09cac
"""
from __future__ import annotations



def solve(grid):
    """Scale each cell to a 2x2 block."""
    out = []
    for row in grid:
        new_row = []
        for v in row:
            new_row.extend([v, v])
        out.append(new_row)
        out.append(new_row[:])
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
