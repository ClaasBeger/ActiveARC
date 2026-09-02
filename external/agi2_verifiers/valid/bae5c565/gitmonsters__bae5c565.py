"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: bae5c565
source: GitMonsters/SOLVED-562-verified
original_path: solves/bae5c565/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__bae5c565
"""
from __future__ import annotations



"""ARC-AGI puzzle bae5c565 solver.

Rule: Row 0 contains a color pattern with background(5) at the cyan column position.
A vertical cyan(8) line acts as the axis. The pattern from row 0 is "draped" as an
expanding triangle from the top of the cyan line downward, adding one more column
on each side per row, capped at the grid edges. Row 0 is cleared to background.
"""

def transform(input_grid: list[list[int]]) -> list[list[int]]:
    rows = len(input_grid)
    cols = len(input_grid[0])
    bg = 5

    # Find the vertical cyan(8) line (skip row 0 which is the pattern)
    cyan_col = None
    cyan_start = None
    for c in range(cols):
        start = None
        count = 0
        for r in range(1, rows):
            if input_grid[r][c] == 8:
                if start is None:
                    start = r
                count += 1
        if count >= 2:
            cyan_col = c
            cyan_start = start
            break

    pattern = input_grid[0][:]

    # Build output filled with background
    output = [[bg] * cols for _ in range(rows)]

    # Place cyan line and expanding pattern
    for r in range(cyan_start, rows):
        output[r][cyan_col] = 8
        expansion = r - cyan_start
        for i in range(1, min(expansion, cyan_col) + 1):
            output[r][cyan_col - i] = pattern[cyan_col - i]
        for i in range(1, min(expansion, cols - 1 - cyan_col) + 1):
            output[r][cyan_col + i] = pattern[cyan_col + i]

    return output




# Catalog entry point: every solver in solves/ exposes solve(grid).
def solve(grid):
    return [list(row) for row in transform(grid)]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
