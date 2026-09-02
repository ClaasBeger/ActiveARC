"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: c64f1187
source: GitMonsters/SOLVED-562-verified
original_path: solves/c64f1187/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__c64f1187
"""
from __future__ import annotations



"""Solver for ARC-AGI task c64f1187.

Pattern:
- Top section has color markers with 2x2 shape templates (1s) below-right.
- Bottom section has a grid of 2x2 cells (5s) with color tags.
- Output replaces each tagged cell with its color's shape template.
"""

from typing import List

Grid = List[List[int]]


def solve(grid: Grid) -> Grid:
    rows = len(grid)
    cols = len(grid[0])

    # Step 1: Find color-shape mapping from the template section
    # Shapes are made of 1s; the color marker sits one row above, one col left
    one_positions = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 1]
    shape_min_r = min(r for r, _ in one_positions)
    color_marker_row = shape_min_r - 1

    color_shapes: dict[int, list[list[int]]] = {}
    for c in range(cols):
        val = grid[color_marker_row][c]
        if val not in (0, 1, 5):
            shape = [
                [grid[shape_min_r + dr][c + 1 + dc] for dc in range(2)]
                for dr in range(2)
            ]
            color_shapes[val] = shape

    # Step 2: Locate the grid of 2x2 cells made of 5s
    five_positions = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 5]
    min_r = min(r for r, _ in five_positions)
    min_c = min(c for _, c in five_positions)
    max_r = max(r for r, _ in five_positions)
    max_c = max(c for _, c in five_positions)

    # Cells are 2x2 with 1-wide gaps → stride of 3
    cell_rows = list(range(min_r, max_r + 1, 3))
    cell_cols = list(range(min_c, max_c + 1, 3))

    # Step 3: Read color from each cell (non-5, non-0 value, or 0 if blank)
    cell_colors = []
    for cr in cell_rows:
        row_colors = []
        for cc in cell_cols:
            color = 0
            for dr in range(2):
                for dc in range(2):
                    v = grid[cr + dr][cc + dc]
                    if v not in (0, 5):
                        color = v
            row_colors.append(color)
        cell_colors.append(row_colors)

    # Step 4: Build output — same cell grid but shapes instead of 5-blocks
    nr, nc = len(cell_rows), len(cell_cols)
    out_h = nr * 2 + (nr - 1)
    out_w = nc * 2 + (nc - 1)
    output = [[0] * out_w for _ in range(out_h)]

    for ri in range(nr):
        for ci in range(nc):
            color = cell_colors[ri][ci]
            if color == 0:
                continue
            shape = color_shapes[color]
            or_ = ri * 3
            oc = ci * 3
            for dr in range(2):
                for dc in range(2):
                    if shape[dr][dc] == 1:
                        output[or_ + dr][oc + dc] = color

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
