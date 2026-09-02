"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e74e1818
source: GitMonsters/SOLVED-562-verified
original_path: solves/e74e1818/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__e74e1818
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """Reverse the row order within each contiguous single-color row group."""
    import copy
    result = copy.deepcopy(grid)
    rows = len(grid)

    def row_color(row):
        for val in row:
            if val != 0:
                return val
        return 0

    i = 0
    while i < rows:
        color = row_color(grid[i])
        if color == 0:
            i += 1
            continue
        j = i
        while j < rows and row_color(grid[j]) == color:
            j += 1
        # Reverse this group's rows
        group = [grid[r][:] for r in range(i, j)]
        group.reverse()
        for k, r in enumerate(range(i, j)):
            result[r] = group[k]
        i = j

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
