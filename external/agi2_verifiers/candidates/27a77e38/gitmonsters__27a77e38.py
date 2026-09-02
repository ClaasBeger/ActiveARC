"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 27a77e38
source: GitMonsters/SOLVED-562-verified
original_path: solves/27a77e38/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__27a77e38
"""
from __future__ import annotations



def solve(grid):
    # Above the all-5s row is a pattern. Find the most frequent value.
    # Place it at the center of the bottom-most row.
    rows, cols = len(grid), len(grid[0])
    result = [row[:] for row in grid]

    # Find the all-5s row
    five_row = None
    for r in range(rows):
        if all(grid[r][c] == 5 for c in range(cols)):
            five_row = r
            break

    # Count values above the 5s row
    from collections import Counter
    counts = Counter()
    for r in range(five_row):
        for c in range(cols):
            v = grid[r][c]
            if v != 0 and v != 5:
                counts[v] += 1

    # Most frequent value
    most_freq = counts.most_common(1)[0][0]

    # Place at center of bottom-most row
    center_col = cols // 2
    result[rows - 1][center_col] = most_freq

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
