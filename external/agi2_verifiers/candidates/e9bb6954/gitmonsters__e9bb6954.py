"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e9bb6954
source: GitMonsters/SOLVED-562-verified
original_path: solves/e9bb6954/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__e9bb6954
"""
from __future__ import annotations



"""Solver for ARC-AGI puzzle e9bb6954.

Pattern: Each 3x3 monochrome block emits a cross (full row + full column)
through its center, using the block's color. At intersections of lines
from different blocks, the cell is set to 0.
"""

import json
import copy


def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    output = copy.deepcopy(grid)

    # Find all 3x3 monochrome blocks by their center
    centers: list[tuple[int, int, int]] = []
    seen: set[tuple[int, int, int]] = set()
    for r in range(rows - 2):
        for c in range(cols - 2):
            color = grid[r][c]
            if color == 0:
                continue
            if all(grid[r + dr][c + dc] == color for dr in range(3) for dc in range(3)):
                center = (r + 1, c + 1, color)
                if center not in seen:
                    seen.add(center)
                    centers.append(center)

    # Draw cross lines from each block center
    for cr, cc, color in centers:
        for c in range(cols):
            output[cr][c] = color
        for r in range(rows):
            output[r][cc] = color

    # At intersections of lines from different blocks, set cell to 0
    for i, (cr1, cc1, _) in enumerate(centers):
        for j, (cr2, cc2, _) in enumerate(centers):
            if i != j:
                output[cr1][cc2] = 0
                output[cr2][cc1] = 0

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
