"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 5751f35e
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[184](id=184)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0184__5751f35e
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid_lst: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid_lst)
    height, width = grid.shape
    center_r = (height - 1) / 2.0
    center_c = (width - 1) / 2.0

    colors = np.unique(grid[grid != 0])

    layers = []
    for color in colors:
        positions = np.argwhere(grid == color)
        min_r = positions[:, 0].min()
        max_r = positions[:, 0].max()
        min_c = positions[:, 1].min()
        max_c = positions[:, 1].max()

        h = max_r - min_r + 1
        w = max_c - min_c + 1
        if h != w:
            diff = abs(h - w)
            if h < w:
                old_center = (min_r + max_r) / 2.0
                add_min_center = old_center - diff / 2.0
                add_max_center = old_center + diff / 2.0
                dist_min = abs(add_min_center - center_r)
                dist_max = abs(add_max_center - center_r)
                if dist_min < dist_max:
                    min_r -= diff
                else:
                    max_r += diff
            else:
                old_center = (min_c + max_c) / 2.0
                add_min_center = old_center - diff / 2.0
                add_max_center = old_center + diff / 2.0
                dist_min = abs(add_min_center - center_c)
                dist_max = abs(add_max_center - center_c)
                if dist_min < dist_max:
                    min_c -= diff
                else:
                    max_c += diff

        side = max_r - min_r + 1
        layers.append({'color': color, 'min_r': min_r, 'max_r': max_r, 'min_c': min_c, 'max_c': max_c, 'side': side})

    # Sort by side ascending
    layers.sort(key=lambda x: x['side'])

    output = np.copy(grid)

    for i, layer in enumerate(layers):
        if i == 0:
            # Fill entire box
            for r in range(layer['min_r'], layer['max_r'] + 1):
                for c in range(layer['min_c'], layer['max_c'] + 1):
                    if 0 <= r < height and 0 <= c < width and output[r, c] == 0:
                        output[r, c] = layer['color']
        else:
            prev = layers[i - 1]
            for r in range(layer['min_r'], layer['max_r'] + 1):
                for c in range(layer['min_c'], layer['max_c'] + 1):
                    if not (prev['min_r'] <= r <= prev['max_r'] and prev['min_c'] <= c <= prev['max_c']):
                        if 0 <= r < height and 0 <= c < width and output[r, c] == 0:
                            output[r, c] = layer['color']

    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
