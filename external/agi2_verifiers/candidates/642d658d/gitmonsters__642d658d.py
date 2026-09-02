"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 642d658d
source: GitMonsters/SOLVED-562-verified
original_path: solves/642d658d/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__642d658d
"""
from __future__ import annotations



from collections import Counter

def solve(grid: list[list[int]]) -> list[list[int]]:
    rows, cols = len(grid), len(grid[0])
    arm_colors = []

    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if grid[r][c] == 4:
                up, down, left, right = grid[r-1][c], grid[r+1][c], grid[r][c-1], grid[r][c+1]
                if up == down == left == right and up != 4:
                    arm_colors.append(up)

    most_common = Counter(arm_colors).most_common(1)[0][0]
    return [[most_common]]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
