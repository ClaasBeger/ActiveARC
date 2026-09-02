"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 88207623
source: GitMonsters/SOLVED-562-verified
original_path: solves/88207623/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__88207623
"""
from __future__ import annotations



"""
Solver for ARC-AGI task 88207623.

Pattern: Each shape group has a vertical line of 2s (mirror axis), 4-cells on one
side forming a pattern, and a single colored marker on the opposite side. The
solution reflects the 4-pattern across the 2-line, filling mirrored positions
with the marker's color. Internal holes (0s within the shape) are preserved.
"""

import json
import copy
from typing import List

Grid = List[List[int]]


def solve(grid: Grid) -> Grid:
    rows = len(grid)
    cols = len(grid[0])
    result = copy.deepcopy(grid)

    # Find all 2-cells
    two_cells = set()
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                two_cells.add((r, c))

    # Group 2-cells into vertical lines (connected vertically in same column)
    visited: set = set()
    two_lines = []
    for r, c in sorted(two_cells):
        if (r, c) in visited:
            continue
        group = []
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if (cr, cc) in visited or (cr, cc) not in two_cells:
                continue
            visited.add((cr, cc))
            group.append((cr, cc))
            for dr in [-1, 1]:
                nr = cr + dr
                if 0 <= nr < rows and (nr, cc) in two_cells:
                    stack.append((nr, cc))
        two_lines.append(sorted(group))

    # Process each 2-line
    for line in two_lines:
        col_2 = line[0][1]
        row_min = line[0][0]
        row_max = line[-1][0]

        # Count 4-cells on each side (stop at any 2-barrier)
        left_4s = 0
        right_4s = 0
        for r in range(row_min, row_max + 1):
            for d in range(1, cols):
                c = col_2 - d
                if c < 0 or grid[r][c] == 2:
                    break
                if grid[r][c] == 4:
                    left_4s += 1
            for d in range(1, cols):
                c = col_2 + d
                if c >= cols or grid[r][c] == 2:
                    break
                if grid[r][c] == 4:
                    right_4s += 1

        if left_4s == 0 and right_4s == 0:
            continue

        four_dir = -1 if left_4s >= right_4s else 1
        mirror_dir = -four_dir

        # Find color marker on the mirror side (non-0, non-2, non-4)
        color = None
        for r in range(row_min, row_max + 1):
            for d in range(1, cols):
                c = col_2 + mirror_dir * d
                if c < 0 or c >= cols:
                    break
                if grid[r][c] == 2:
                    break
                if grid[r][c] not in (0, 4):
                    color = grid[r][c]
                    break
            if color is not None:
                break

        if color is None:
            continue

        # Mirror the 4-shape across the 2-line for each row
        for r in range(row_min, row_max + 1):
            # Find max extent of 4-cells in this row (stop at 2-barrier)
            max_dist = 0
            for d in range(1, cols):
                fc = col_2 + four_dir * d
                if fc < 0 or fc >= cols:
                    break
                if grid[r][fc] == 2:
                    break
                if grid[r][fc] == 4:
                    max_dist = d

            # Mirror: where there's a 4, place the color on the opposite side
            for d in range(1, max_dist + 1):
                fc = col_2 + four_dir * d
                mc = col_2 + mirror_dir * d
                if 0 <= fc < cols and 0 <= mc < cols:
                    if grid[r][fc] == 4:
                        result[r][mc] = color

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
