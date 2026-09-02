"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ce8d95cc
source: GitMonsters/SOLVED-562-verified
original_path: solves/ce8d95cc/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__ce8d95cc
"""
from __future__ import annotations



"""Solver for ARC-AGI task ce8d95cc.

Pattern: The grid has divider rows (all non-zero) and divider columns (all non-zero).
These partition the grid into rectangular regions. The output compresses each region
to a single cell, preserving divider rows/columns as single rows/columns.
"""

import json


def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])

    divider_rows = [r for r in range(rows) if all(grid[r][c] != 0 for c in range(cols))]
    divider_cols = [c for c in range(cols) if all(grid[r][c] != 0 for r in range(rows))]

    def make_groups(dividers: list[int], total: int) -> list[list[int]]:
        groups = []
        prev = 0
        for d in dividers:
            if prev < d:
                groups.append([prev])  # representative index for region
            groups.append([d])         # divider kept as-is
            prev = d + 1
        if prev < total:
            groups.append([prev])
        return groups

    row_groups = make_groups(divider_rows, rows)
    col_groups = make_groups(divider_cols, cols)

    return [[grid[rg[0]][cg[0]] for cg in col_groups] for rg in row_groups]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
