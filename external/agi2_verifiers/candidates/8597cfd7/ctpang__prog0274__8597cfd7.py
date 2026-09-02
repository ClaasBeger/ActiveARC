"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 8597cfd7
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[274](id=274)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0274__8597cfd7
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    rows, cols = grid.shape
    # Find grey row
    grey_row = next(i for i in range(rows) if np.all(grid[i] == 5))
    # Find colors and their columns
    color_cols = {}
    for c in range(cols):
        for r in range(rows):
            if grid[r, c] != 0 and grid[r, c] != 5:
                color = grid[r, c]
                if color not in color_cols:
                    color_cols[color] = c
                elif color_cols[color] != c:
                    raise ValueError("Multiple columns for color")
    colors = list(color_cols.keys())
    # Compute deltas
    heights = {}
    for color in colors:
        col = color_cols[color]
        # Above
        above_rows = [r for r in range(grey_row) if grid[r, col] == color]
        h_above = (max(above_rows) - min(above_rows) + 1) if above_rows else 0
        # Below
        below_rows = [r for r in range(grey_row + 1, rows) if grid[r, col] == color]
        h_below = (max(below_rows) - min(below_rows) + 1) if below_rows else 0
        delta = h_below - h_above
        heights[color] = delta
    # Find winner
    max_delta = max(heights.values())
    winners = [c for c, d in heights.items() if d == max_delta]
    win_color = winners[0]
    # Return 2x2 of win_color
    return [[win_color, win_color], [win_color, win_color]]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
