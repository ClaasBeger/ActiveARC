"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: c3202e5a
source: GitMonsters/SOLVED-562-verified
original_path: solves/c3202e5a/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__c3202e5a
"""
from __future__ import annotations



def solve(grid):
    """Grid divided by separator lines. Return section with fewest distinct non-zero colors."""
    rows = len(grid)
    cols = len(grid[0])

    # Find separator value: the value that forms complete rows
    from collections import Counter
    sep_val = None
    for r in range(rows):
        if len(set(grid[r])) == 1 and grid[r][0] != 0:
            sep_val = grid[r][0]
            break

    # Find separator rows and cols
    sep_rows = [r for r in range(rows) if all(grid[r][c] == sep_val for c in range(cols))]
    sep_cols = [c for c in range(cols) if all(grid[r][c] == sep_val for r in range(rows))]

    def ranges_from_seps(seps, total):
        boundaries = [-1] + seps + [total]
        result = []
        for i in range(len(boundaries) - 1):
            start = boundaries[i] + 1
            end = boundaries[i + 1]
            if start < end:
                result.append((start, end))
        return result

    row_ranges = ranges_from_seps(sep_rows, rows)
    col_ranges = ranges_from_seps(sep_cols, cols)

    best_section = None
    best_count = float('inf')

    for rs, re in row_ranges:
        for cs, ce in col_ranges:
            colors = set()
            for r in range(rs, re):
                for c in range(cs, ce):
                    if grid[r][c] != 0:
                        colors.add(grid[r][c])
            count = len(colors)
            if 0 < count < best_count:
                best_count = count
                best_section = [[grid[r][c] for c in range(cs, ce)] for r in range(rs, re)]

    return best_section

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
