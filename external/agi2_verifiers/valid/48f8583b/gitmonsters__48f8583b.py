"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 48f8583b
source: GitMonsters/SOLVED-562-verified
original_path: solves/48f8583b/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__48f8583b
"""
from __future__ import annotations



"""Solver for ARC task 48f8583b.

Rule: Find the least frequent color in the 3x3 input. Create a 9x9 grid
(3x3 arrangement of 3x3 blocks). Place copies of the input at the block
positions corresponding to cells containing the least frequent color.
"""
import json
from collections import Counter


def solve(grid: list[list[int]]) -> list[list[int]]:
    n = len(grid)
    counts = Counter(val for row in grid for val in row)
    min_color = min(counts, key=counts.get)

    output = [[0] * (n * n) for _ in range(n * n)]
    for r in range(n):
        for c in range(n):
            if grid[r][c] == min_color:
                for dr in range(n):
                    for dc in range(n):
                        output[r * n + dr][c * n + dc] = grid[dr][dc]
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
