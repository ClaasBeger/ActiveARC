"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: b7256dcd
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[383](id=383)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0383__b7256dcd
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid

    height = len(grid)
    width = len(grid[0])
    output = [row[:] for row in grid]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def flood_fill(start_r, start_c, col):
        if output[start_r][start_c] != 6:
            return
        stack = [(start_r, start_c)]
        while stack:
            cr, cc = stack.pop()
            if output[cr][cc] == 6:
                output[cr][cc] = col
                for dr, dc in directions:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width:
                        stack.append((nr, nc))

    # Find sources
    sources = []
    for r in range(height):
        for c in range(width):
            if output[r][c] != 7 and output[r][c] != 6:
                sources.append((r, c, output[r][c]))

    # Paint for each source
    for r, c, col in sources:
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < height and 0 <= nc < width and output[nr][nc] == 6:
                flood_fill(nr, nc, col)

    # Set sources to 7
    for r, c, col in sources:
        output[r][c] = 7

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
