"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 5d588b4d
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[196](id=196)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0196__5d588b4d
"""
from __future__ import annotations



import numpy as np

import math

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    cols = len(grid[0])
    # Find C and L from top row
    top = grid[0]
    C = 0
    L = 0
    for i in range(cols):
        if top[i] != 0:
            if C == 0:
                C = top[i]
            if top[i] == C:
                L += 1
            else:
                break
    if L == 0:
        return [[0] * cols]
    # Generate groups
    groups = list(range(1, L + 1)) + list(range(1, L))[::-1]
    # Generate sequence
    sequence = []
    for k in groups:
        sequence.extend([C] * k)
        sequence.append(0)
    # Calculate output height
    seq_len = len(sequence)
    height = math.ceil(seq_len / cols)
    # Build output
    output = []
    for r in range(height):
        start = r * cols
        end = min(start + cols, seq_len)
        row = sequence[start:end] + [0] * (cols - (end - start))
        output.append(row)
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
