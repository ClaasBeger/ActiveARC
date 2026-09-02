"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 17b80ad2
source: GitMonsters/SOLVED-562-verified
original_path: solves/17b80ad2/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__17b80ad2
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    import copy
    result = copy.deepcopy(grid)
    rows = len(grid)
    cols = len(grid[0])
    last_row = rows - 1

    # Find columns marked with 5 in the last row
    marked_cols = [c for c in range(cols) if grid[last_row][c] == 5]

    for c in marked_cols:
        # Collect all non-zero values in this column, sorted by row
        values = [(r, grid[r][c]) for r in range(rows) if grid[r][c] != 0]

        # Fill segments: each value fills upward from previous value's row+1 to its own row
        prev_row = -1
        for r, v in values:
            for fill_r in range(prev_row + 1, r + 1):
                result[fill_r][c] = v
            prev_row = r

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
