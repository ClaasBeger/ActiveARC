"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 5af49b42
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[190](id=190)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0190__5af49b42
"""
from __future__ import annotations



import numpy as np

import copy

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    palettes = []
    seeds = []
    for r in range(rows):
        c = 0
        while c < cols:
            if grid[r][c] == 0:
                c += 1
                continue
            start = c
            seq = []
            while c < cols and grid[r][c] != 0:
                seq.append(grid[r][c])
                c += 1
            if len(seq) == 1:
                seeds.append((r, start, seq[0]))
            elif len(seq) >= 2:
                palettes.append(seq)
    output = copy.deepcopy(grid)
    for r, c, color in seeds:
        for pal in palettes:
            if color in pal:
                i = pal.index(color)
                start_c = c - i
                for j in range(len(pal)):
                    place_c = start_c + j
                    if 0 <= place_c < cols:
                        output[r][place_c] = pal[j]
                break
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
