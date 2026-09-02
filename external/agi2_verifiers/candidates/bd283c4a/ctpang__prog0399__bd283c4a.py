"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: bd283c4a
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[399](id=399)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0399__bd283c4a
"""
from __future__ import annotations



import numpy as np

from collections import Counter

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    height = len(grid)
    width = len(grid[0])
    
    # Collect frequencies
    counter = Counter()
    for row in grid:
        for cell in row:
            counter[cell] += 1
    
    # Sort colors by decreasing frequency, then by increasing color number if tie
    color_list = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
    
    # Positions in order: left to right, bottom to top within column
    positions = [(c, r) for c in range(width) for r in range(height - 1, -1, -1)]
    
    # Create output grid
    output = [[0] * width for _ in range(height)]
    
    # Fill the output
    idx = 0
    for colr, count in color_list:
        for _ in range(count):
            c, r = positions[idx]
            output[r][c] = colr
            idx += 1
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
