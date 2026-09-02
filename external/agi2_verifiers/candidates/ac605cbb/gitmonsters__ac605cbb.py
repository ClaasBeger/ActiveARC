"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ac605cbb
source: GitMonsters/SOLVED-562-verified
original_path: solves/ac605cbb/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__ac605cbb
"""
from __future__ import annotations



"""
ARC-AGI solver for task ac605cbb.

Each colored dot spawns an arm whose length and direction are determined by its color:
  1 → L-shape: right 2 then up 1
  2 → left 4
  3 → down 3
  6 → up 6
Arm cells between origin and copy are filled with 5.
When two arm bodies intersect, the cell becomes 4 and a SW diagonal of 4s
extends to the grid boundary.
"""

import json
from typing import List

Grid = List[List[int]]

ARM_SPECS = {
    1: {"body_offsets": [(0, 1), (0, 2)], "copy_offset": (-1, 2)},
    2: {"body_offsets": [(0, -1), (0, -2), (0, -3)], "copy_offset": (0, -4)},
    3: {"body_offsets": [(1, 0), (2, 0)], "copy_offset": (3, 0)},
    6: {"body_offsets": [(-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0)], "copy_offset": (-6, 0)},
}


def solve(grid: Grid) -> Grid:
    rows, cols = len(grid), len(grid[0])

    # Locate all colored dots
    dots = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                dots.append((r, c, grid[r][c]))

    # Compute arm body cells and copy cells
    arms = []  # (body_cells, copy_cell, color)
    for r, c, color in dots:
        spec = ARM_SPECS.get(color)
        if spec is None:
            continue
        body = [
            (r + dr, c + dc)
            for dr, dc in spec["body_offsets"]
            if 0 <= r + dr < rows and 0 <= c + dc < cols
        ]
        cr, cc = r + spec["copy_offset"][0], c + spec["copy_offset"][1]
        copy_cell = (cr, cc) if 0 <= cr < rows and 0 <= cc < cols else None
        arms.append((body, copy_cell, color))

    # Detect intersections (body cells claimed by ≥2 arms)
    cell_count: dict[tuple[int, int], int] = {}
    for body, _, _ in arms:
        for cell in body:
            cell_count[cell] = cell_count.get(cell, 0) + 1
    intersections = {cell for cell, cnt in cell_count.items() if cnt >= 2}

    # Build output layer by layer (later layers overwrite earlier ones)
    out: Grid = [[0] * cols for _ in range(rows)]

    # 1. Arm body fills (5)
    for body, _, _ in arms:
        for br, bc in body:
            out[br][bc] = 5

    # 2. Copy endpoints
    for _, copy_cell, color in arms:
        if copy_cell is not None:
            out[copy_cell[0]][copy_cell[1]] = color

    # 3. Intersections → 4, plus SW diagonal of 4s to grid edge
    for ir, ic in intersections:
        out[ir][ic] = 4
        r, c = ir + 1, ic - 1
        while 0 <= r < rows and 0 <= c < cols:
            if out[r][c] in (0, 5):
                out[r][c] = 4
            r += 1
            c -= 1

    # 4. Original dots (highest priority, always preserved)
    for r, c, color in dots:
        out[r][c] = color

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
