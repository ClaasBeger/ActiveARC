"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e1baa8a4
source: GitMonsters/SOLVED-562-verified
original_path: solves/e1baa8a4/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__e1baa8a4
"""
from __future__ import annotations



def solve(grid):
    rows = len(grid)
    cols = len(grid[0])

    # Find row boundaries from column 0
    row_bounds = [0]
    for r in range(1, rows):
        if grid[r][0] != grid[r - 1][0]:
            row_bounds.append(r)

    # Find col boundaries from row 0
    col_bounds = [0]
    for c in range(1, cols):
        if grid[0][c] != grid[0][c - 1]:
            col_bounds.append(c)

    out = []
    for rb in row_bounds:
        row = []
        for cb in col_bounds:
            row.append(grid[rb][cb])
        out.append(row)
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
