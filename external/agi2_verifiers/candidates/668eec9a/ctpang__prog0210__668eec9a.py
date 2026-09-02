"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 668eec9a
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[210](id=210)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0210__668eec9a
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid_lst: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid_lst)
    height, width = grid.shape
    background = grid[0, 0]
    
    all_colors = set(grid.flatten())
    trail_colors = [c for c in all_colors if c != background]
    
    min_rows = []
    for color in trail_colors:
        positions = np.argwhere(grid == color)
        min_r = positions[:, 0].min()
        min_rows.append((min_r, color))
    
    min_rows.sort()
    colors = [c for _, c in min_rows]
    
    num_layers = len(colors)
    pad = 5 - num_layers
    
    output = []
    for _ in range(pad):
        output.append([background] * 3)
    for c in colors:
        output.append([c] * 3)
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
