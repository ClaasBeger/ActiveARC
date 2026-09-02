"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: a406ac07
source: GitMonsters/SOLVED-562-verified
original_path: solves/a406ac07/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__a406ac07
"""
from __future__ import annotations



"""
Task a406ac07: Diagonal block fill from border labels.

The right column and bottom row encode color labels. Consecutive same-color
groups define row/column spans. Each matching color group fills a diagonal
rectangle at the intersection of its row span and column span.
"""
import json


def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    result = [row[:] for row in grid]

    right_col = [grid[r][cols - 1] for r in range(rows)]
    bottom_row = [grid[rows - 1][c] for c in range(cols)]

    def group_consecutive(arr: list[int]) -> list[tuple[int, int, int]]:
        groups = []
        i = 0
        while i < len(arr):
            color = arr[i]
            j = i
            while j < len(arr) and arr[j] == color:
                j += 1
            groups.append((color, i, j - 1))
            i = j
        return groups

    rc_groups = group_consecutive(right_col)
    br_groups = group_consecutive(bottom_row)

    for (rc_color, r_start, r_end), (br_color, c_start, c_end) in zip(rc_groups, br_groups):
        color = rc_color
        for r in range(r_start, r_end + 1):
            for c in range(c_start, c_end + 1):
                result[r][c] = color

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
