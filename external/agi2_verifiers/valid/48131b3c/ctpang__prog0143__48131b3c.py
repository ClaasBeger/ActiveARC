"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 48131b3c
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[143](id=143)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0143__48131b3c
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid:
        return []
    n = len(grid)
    # Assume square grid
    assert all(len(row) == n for row in grid)
    
    # Find the non-zero color C
    colors = set()
    for row in grid:
        for val in row:
            if val != 0:
                colors.add(val)
    assert len(colors) == 1
    c = next(iter(colors))
    
    # Create inverted grid
    inverted = []
    for row in grid:
        new_row = [c if x == 0 else 0 for x in row]
        inverted.append(new_row)
    
    # Tile horizontally twice
    horiz_tiled = []
    for row in inverted:
        horiz_tiled.append(row + row)
    
    # Tile vertically twice
    output = horiz_tiled + horiz_tiled
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
