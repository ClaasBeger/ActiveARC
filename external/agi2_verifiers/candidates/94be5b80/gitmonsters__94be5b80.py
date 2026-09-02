"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 94be5b80
source: GitMonsters/SOLVED-562-verified
original_path: solves/94be5b80/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__94be5b80
"""
from __future__ import annotations



"""Solver for ARC-AGI task 94be5b80.

Pattern: A color key (3 identical rows of distinct colors) defines the
top-to-bottom stacking order of identical shapes. Existing shapes in the
input provide the template; missing colors get new copies placed in order.
"""

import json
from typing import List

Grid = List[List[int]]


def solve(grid: Grid) -> Grid:
    rows, cols = len(grid), len(grid[0])

    # 1. Find key: 3 consecutive identical rows with ≥2 distinct non-zero values
    key_colors = key_row_start = key_col_start = key_col_end = None
    for r in range(rows - 2):
        if grid[r] == grid[r + 1] == grid[r + 2]:
            nz = [(c, grid[r][c]) for c in range(cols) if grid[r][c] != 0]
            if len(nz) >= 2 and len(set(v for _, v in nz)) == len(nz):
                cs = [c for c, _ in nz]
                if cs[-1] - cs[0] + 1 == len(cs):  # contiguous
                    key_colors = [v for _, v in nz]
                    key_row_start, key_col_start, key_col_end = r, cs[0], cs[-1]
                    break

    # 2. Mark key cells for exclusion
    key_cells = {
        (r, c)
        for r in range(key_row_start, key_row_start + 3)
        for c in range(key_col_start, key_col_end + 1)
    }

    # 3. Find existing shapes (cells of each key color, excluding key area)
    shapes = {}
    for color in key_colors:
        cells = [
            (r, c)
            for r in range(rows)
            for c in range(cols)
            if grid[r][c] == color and (r, c) not in key_cells
        ]
        if cells:
            shapes[color] = cells

    # 4. Build template from first (topmost) existing shape
    ref_color = min(shapes, key=lambda c: min(r for r, _ in shapes[c]))
    ref_cells = shapes[ref_color]
    ref_min_r = min(r for r, c in ref_cells)
    ref_min_c = min(c for r, c in ref_cells)

    template = [(r - ref_min_r, c - ref_min_c) for r, c in ref_cells]
    shape_height = max(r for r, c in ref_cells) - ref_min_r + 1
    col_offset = ref_min_c

    # 5. Calculate base row for the entire stack
    ref_idx = key_colors.index(ref_color)
    base_row = ref_min_r - ref_idx * shape_height

    # 6. Build output: place all shapes
    out = [[0] * cols for _ in range(rows)]
    for i, color in enumerate(key_colors):
        start_row = base_row + i * shape_height
        for dr, dc in template:
            r, c = start_row + dr, col_offset + dc
            if 0 <= r < rows and 0 <= c < cols:
                out[r][c] = color

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
