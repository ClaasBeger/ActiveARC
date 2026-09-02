"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 95a58926
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[313](id=313)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0313__95a58926
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid

    rows = len(grid)
    cols = len(grid[0])

    # Find accent color: any color not 0 or 5
    colors = set()
    for row in grid:
        for cell in row:
            if cell != 0 and cell != 5:
                colors.add(cell)

    if len(colors) != 1:
        return grid  # Assume one accent color per examples

    accent = list(colors)[0]

    # Find horizontal rows: all cells ==5 or ==accent
    horiz_rows = []
    for r in range(rows):
        if all(cell == 5 or cell == accent for cell in grid[r]):
            horiz_rows.append(r)

    # Find vertical columns: all cells ==5 or ==accent
    vert_cols = []
    for c in range(cols):
        if all(grid[r][c] == 5 or grid[r][c] == accent for r in range(rows)):
            vert_cols.append(c)

    # Create output
    output = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            is_horiz = r in horiz_rows
            is_vert = c in vert_cols
            if is_horiz and is_vert:
                output[r][c] = accent
            elif is_horiz or is_vert:
                output[r][c] = 5

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
