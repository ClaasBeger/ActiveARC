"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: bbb1b8b6
source: GitMonsters/SOLVED-562-verified
original_path: solves/bbb1b8b6/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__bbb1b8b6
"""
from __future__ import annotations



"""
ARC-AGI task bbb1b8b6 solver.

Rule: Input is 4x9 split by a column of 5s into left (cols 0-3) and right (cols 5-8).
- Left has a shape made of 1s (and 0s).
- Right has a shape made of a single color (and 0s).
- If the right's non-zero positions exactly equal the left's zero positions,
  fill those zeros with the right's color.
- Otherwise, output = left unchanged.
"""

from typing import List

Grid = List[List[int]]


def solve(grid: Grid) -> Grid:
    rows = len(grid)
    # Find separator column (all 5s)
    sep = next(c for c in range(len(grid[0])) if all(grid[r][c] == 5 for r in range(rows)))
    left = [row[:sep] for row in grid]
    right = [row[sep + 1:] for row in grid]

    left_zeros = {(r, c) for r in range(rows) for c in range(len(left[0])) if left[r][c] == 0}
    right_nonzero = {(r, c) for r in range(rows) for c in range(len(right[0])) if right[r][c] != 0}

    if left_zeros == right_nonzero:
        # Fill zeros with the right-side color
        return [
            [right[r][c] if left[r][c] == 0 else left[r][c] for c in range(len(left[0]))]
            for r in range(rows)
        ]
    else:
        return [row[:] for row in left]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
