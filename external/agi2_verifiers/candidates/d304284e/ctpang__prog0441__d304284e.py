"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: d304284e
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[441](id=441)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0441__d304284e
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    rows = len(grid)
    cols = len(grid[0])
    
    # Find bounding box
    min_r, max_r, min_c, max_c = rows, -1, cols, -1
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                min_r = min(min_r, r)
                max_r = max(max_r, r)
                min_c = min(min_c, c)
                max_c = max(max_c, c)
    
    if min_r == rows:
        return grid  # no shape
    
    h = max_r - min_r + 1
    w = max_c - min_c + 1
    
    # Output grid
    output = [[0] * cols for _ in range(rows)]
    
    # Horizontal row
    six_positions = []
    i = 0
    while True:
        start_c = min_c + i * (w + 1)
        if start_c >= cols:
            break
        color = 6 if i % 3 == 2 else 7
        if color == 6:
            six_positions.append(start_c)
        for rel_r in range(h):
            abs_r = min_r + rel_r
            if abs_r >= rows:
                break
            for rel_c in range(w):
                abs_c = start_c + rel_c
                if abs_c >= cols:
                    break
                orig_val = grid[min_r + rel_r][min_c + rel_c]
                if orig_val != 0:
                    output[abs_r][abs_c] = color
        i += 1
    
    # Vertical stacks for 6 positions
    for start_c in six_positions:
        j = 1
        while True:
            start_r = min_r + j * (h + 1)
            if start_r >= rows:
                break
            color = 6
            for rel_r in range(h):
                abs_r = start_r + rel_r
                if abs_r >= rows:
                    break
                for rel_c in range(w):
                    abs_c = start_c + rel_c
                    if abs_c >= cols:
                        break
                    orig_val = grid[min_r + rel_r][min_c + rel_c]
                    if orig_val != 0:
                        output[abs_r][abs_c] = color
            j += 1
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
