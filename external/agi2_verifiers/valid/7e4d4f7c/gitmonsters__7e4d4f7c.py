"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 7e4d4f7c
source: GitMonsters/SOLVED-562-verified
original_path: solves/7e4d4f7c/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__7e4d4f7c
"""
from __future__ import annotations



"""ARC-AGI puzzle 7e4d4f7c solver.

Rule: The grid has a pattern row (row 0), a marker row (row 1), and repeated
filler rows. Output is 3 rows: row 0, row 1, and a new row where every
non-background value in row 0 is replaced with 6.
"""


def transform(input_grid: list[list[int]]) -> list[list[int]]:
    row0 = list(input_grid[0])
    row1 = list(input_grid[1])
    background = row1[1]  # dominant fill color
    row2 = [6 if v != background else background for v in row0]
    return [row0, row1, row2]


# --- Verification ---


# Catalog entry point: every solver in solves/ exposes solve(grid).
def solve(grid):
    return [list(row) for row in transform(grid)]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
