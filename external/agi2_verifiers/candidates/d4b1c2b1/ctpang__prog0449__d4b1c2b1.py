"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: d4b1c2b1
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[449](id=449)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0449__d4b1c2b1
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    # Find distinct non-zero colors
    colors = set()
    for row in grid:
        for cell in row:
            if cell != 0:
                colors.add(cell)
    k = len(colors)
    
    # Create output grid of size 3k x 3k initialized to 0
    size = 3 * k
    output = [[0 for _ in range(size)] for _ in range(size)]
    
    # Fill blocks
    for r in range(3):
        for c in range(3):
            color = grid[r][c]
            if color != 0:
                for dr in range(k):
                    for dc in range(k):
                        output[r * k + dr][c * k + dc] = color
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
