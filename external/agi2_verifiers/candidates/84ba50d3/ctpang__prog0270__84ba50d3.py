"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 84ba50d3
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[270](id=270)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0270__84ba50d3
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    output = [row[:] for row in grid]

    # Find red_row
    red_row = None
    for r in range(rows):
        if all(grid[r][c] == 2 for c in range(cols)):
            red_row = r
            break
    if red_row is None:
        return output  # No red row, no change

    # Directions
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Visited
    visited = [[False] * cols for _ in range(rows)]

    # Find components of 1's
    components = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and not visited[r][c]:
                component = []
                stack = [(r, c)]
                visited[r][c] = True
                while stack:
                    cr, cc = stack.pop()
                    component.append((cr, cc))
                    for dr, dc in directions:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1 and not visited[nr][nc]:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                components.append(component)

    # Process each component
    for comp in components:
        if not comp:
            continue
        rs = [pos[0] for pos in comp]
        min_r = min(rs)
        max_r = max(rs)
        height = max_r - min_r + 1

        # Relative cells
        rel_cells = [[] for _ in range(height)]
        for pr, pc in comp:
            rel = pr - min_r
            rel_cells[rel].append(pc)

        # Widths: number of unique c's per rel
        widths = [len(set(rel_cells[rel])) for rel in range(height)]

        # Compute k
        k = 0
        rel = height - 1
        while rel >= 0 and widths[rel] == 1:
            k += 1
            rel -= 1

        # Clear original
        for pr, pc in comp:
            output[pr][pc] = 8

        if k == height:
            # Special: vertical in one col
            col = comp[0][1]  # all same
            d = (rows - 1) - max_r
            for pr, pc in comp:
                new_r = pr + d
                output[new_r][pc] = 1
            output[red_row][col] = 8
        else:
            # Normal
            stopping_rel = height - k - 1
            d = (red_row - 1) - (min_r + stopping_rel)
            for pr, pc in comp:
                new_r = pr + d
                if 0 <= new_r < rows:
                    output[new_r][pc] = 1

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
