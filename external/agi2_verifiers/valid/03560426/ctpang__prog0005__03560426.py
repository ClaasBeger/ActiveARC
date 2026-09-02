"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 03560426
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[5](id=5)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0005__03560426
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    # Find blocks
    blocks = []
    for color in range(1, 10):
        positions = []
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == color:
                    positions.append((r, c))
        if not positions:
            continue
        rs, cs = zip(*positions)
        min_r = min(rs)
        max_r = max(rs)
        min_c = min(cs)
        max_c = max(cs)
        height = max_r - min_r + 1
        width = max_c - min_c + 1
        blocks.append((min_c, color, height, width))
    # Sort by min_c
    blocks.sort()
    # Create output
    output = [[0 for _ in range(cols)] for _ in range(rows)]
    current_right = -1
    current_bottom = -1
    for _, color, h, w in blocks:
        if current_right == -1:
            for cc in range(w):
                for rr in range(h):
                    if rr < rows and cc < cols:
                        output[rr][cc] = color
            current_right = w - 1
            current_bottom = h - 1
        else:
            attach_col = current_right
            # Change the bottom cell
            if current_bottom < rows:
                output[current_bottom][attach_col] = color
            # Add h-1 below
            for i in range(1, h):
                new_r = current_bottom + i
                if new_r < rows:
                    output[new_r][attach_col] = color
            # Update current_bottom
            current_bottom += (h - 1)
            # Add new columns
            start_row = current_bottom - h + 1
            for j in range(1, w):
                new_col = current_right + j
                if new_col >= cols:
                    break
                for rr in range(start_row, current_bottom + 1):
                    if 0 <= rr < rows:
                        output[rr][new_col] = color
            # Update current_right
            current_right += (w - 1)
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
