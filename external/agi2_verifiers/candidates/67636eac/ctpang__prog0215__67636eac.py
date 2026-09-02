"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 67636eac
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[215](id=215)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0215__67636eac
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid_lst: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid_lst)
    height, width = grid.shape
    
    # Find unique non-zero colors
    colors = np.unique(grid[grid > 0])
    
    # Collect shapes
    shapes = []
    for col in colors:
        rs, cs = np.where(grid == col)
        if len(rs) == 0:
            continue
        min_r = rs.min()
        max_r = rs.max()
        min_c = cs.min()
        max_c = cs.max()
        shapes.append({'color': col, 'min_r': min_r, 'max_r': max_r, 'min_c': min_c, 'max_c': max_c})
    
    # Determine mode
    vertical = height > width
    
    # Sort shapes
    if vertical:
        shapes.sort(key=lambda s: s['min_r'])
    else:
        shapes.sort(key=lambda s: s['min_c'])
    
    if not shapes:
        return []
    
    # Assume all have same size
    H = shapes[0]['max_r'] - shapes[0]['min_r'] + 1
    W = shapes[0]['max_c'] - shapes[0]['min_c'] + 1
    num = len(shapes)
    
    if vertical:
        out_height = num * H
        out_width = W
    else:
        out_height = H
        out_width = num * W
    
    out = np.zeros((out_height, out_width), dtype=int)
    
    # Place shapes
    for i, s in enumerate(shapes):
        if vertical:
            start_r = i * H
            start_c = 0
        else:
            start_r = 0
            start_c = i * W
        for dr in range(H):
            for dc in range(W):
                in_r = s['min_r'] + dr
                in_c = s['min_c'] + dc
                out[start_r + dr, start_c + dc] = grid[in_r, in_c]
    
    return out.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
