"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 72207abc
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[242](id=242)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0242__72207abc
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    # Collect cycle of non-zero colors
    cycle = []
    for c in range(cols):
        if grid[1][c] != 0:
            cycle.append(grid[1][c])
    if not cycle:
        return grid
    # Generate positions
    positions = []
    current = 0
    positions.append(current)
    delta = 1
    while True:
        current += delta
        if current >= cols:
            break
        positions.append(current)
        delta += 1
    # Create output grid
    output = [row[:] for row in grid]
    # Set colors cycling through cycle
    for i, pos in enumerate(positions):
        output[1][pos] = cycle[i % len(cycle)]
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
