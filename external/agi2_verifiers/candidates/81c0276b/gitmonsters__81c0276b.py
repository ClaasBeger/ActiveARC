"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 81c0276b
source: GitMonsters/SOLVED-562-verified
original_path: solves/81c0276b/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__81c0276b
"""
from __future__ import annotations



"""
ARC-AGI task 81c0276b solver.

Pattern: The grid is divided into cells by separator lines of a single color.
Each cell contains a 2x2 block of either a content color or the separator color
(meaning "blank"). Count occurrences of each non-separator content color across
all cells, then build a histogram: rows sorted by frequency ascending (least at
top), each row filled left-to-right with the color for `count` cells, rest 0.
"""

import json
from collections import Counter
from typing import List

Grid = List[List[int]]


def solve(grid: Grid) -> Grid:
    rows, cols = len(grid), len(grid[0])

    # Find separator color from fully-filled rows
    sep_color = None
    sep_rows: list[int] = []
    for r in range(rows):
        vals = set(grid[r])
        if len(vals) == 1 and grid[r][0] != 0:
            sep_color = grid[r][0]
            sep_rows.append(r)

    # Find separator columns
    sep_cols: list[int] = []
    for c in range(cols):
        if all(grid[r][c] == sep_color for r in range(rows)):
            sep_cols.append(c)

    # Compute row blocks (ranges between separator rows)
    row_blocks: list[tuple[int, int]] = []
    prev = -1
    for sr in sep_rows:
        if sr > prev + 1:
            row_blocks.append((prev + 1, sr - 1))
        prev = sr
    if prev < rows - 1:
        row_blocks.append((prev + 1, rows - 1))

    # Compute column blocks
    col_blocks: list[tuple[int, int]] = []
    prev = -1
    for sc in sep_cols:
        if sc > prev + 1:
            col_blocks.append((prev + 1, sc - 1))
        prev = sc
    if prev < cols - 1:
        col_blocks.append((prev + 1, cols - 1))

    # For each cell, find the content color (non-zero, non-separator)
    color_counts: Counter = Counter()
    for r_start, r_end in row_blocks:
        for c_start, c_end in col_blocks:
            cell_colors = set()
            for r in range(r_start, r_end + 1):
                for c in range(c_start, c_end + 1):
                    v = grid[r][c]
                    if v != 0 and v != sep_color:
                        cell_colors.add(v)
            if cell_colors:
                color_counts[cell_colors.pop()] += 1

    # Build histogram sorted by count ascending, ties broken by color value
    sorted_colors = sorted(color_counts.items(), key=lambda x: (x[1], x[0]))
    max_count = max(cnt for _, cnt in sorted_colors)

    output: Grid = []
    for color, count in sorted_colors:
        output.append([color] * count + [0] * (max_count - count))

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
