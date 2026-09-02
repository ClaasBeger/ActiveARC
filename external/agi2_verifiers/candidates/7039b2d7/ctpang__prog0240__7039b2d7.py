"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 7039b2d7
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[240](id=240)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0240__7039b2d7
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid_lst: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid_lst)
    rows, cols = grid.shape
    
    # Find colors that form full rows
    row_line_colors = set()
    for r in range(rows):
        val = grid[r, 0]
        if np.all(grid[r, :] == val) and val != 0:
            row_line_colors.add(val)
    
    # Find colors that form full columns
    col_line_colors = set()
    for c in range(cols):
        val = grid[0, c]
        if np.all(grid[:, c] == val) and val != 0:
            col_line_colors.add(val)
    
    # Line color is the intersection (assuming one)
    line_colors = row_line_colors.intersection(col_line_colors)
    line_color = next(iter(line_colors))
    
    # Background is the other non-zero color (assuming two colors total)
    all_colors = set(grid.flatten()) - {0}
    background = (all_colors - {line_color}).pop()
    
    # Find horizontal line positions
    h_lines = [r for r in range(rows) if np.all(grid[r, :] == line_color)]
    h_lines.sort()
    
    # Find vertical line positions
    v_lines = [c for c in range(cols) if np.all(grid[:, c] == line_color)]
    v_lines.sort()
    
    # Count positive row gaps
    num_row_gaps = 0
    prev = -1
    for hl in h_lines:
        start = prev + 1
        end = hl - 1
        if start <= end:
            num_row_gaps += 1
        prev = hl
    # After last
    start = prev + 1
    end = rows - 1
    if start <= end:
        num_row_gaps += 1
    
    # Count positive column gaps
    num_col_gaps = 0
    prev = -1
    for vl in v_lines:
        start = prev + 1
        end = vl - 1
        if start <= end:
            num_col_gaps += 1
        prev = vl
    # After last
    start = prev + 1
    end = cols - 1
    if start <= end:
        num_col_gaps += 1
    
    # Create output grid
    output = [[background for _ in range(num_col_gaps)] for _ in range(num_row_gaps)]
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
