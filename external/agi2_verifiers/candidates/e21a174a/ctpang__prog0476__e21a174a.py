"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e21a174a
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[476](id=476)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0476__e21a174a
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    height = len(grid)
    if height == 0:
        return grid
    width = len(grid[0])
    visited = [[False] * width for _ in range(height)]
    components = []
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]  # 8-way

    for r in range(height):
        for c in range(width):
            if grid[r][c] != 0 and not visited[r][c]:
                color = grid[r][c]
                component_cells = []
                stack = [(r, c)]
                visited[r][c] = True
                min_r = r
                max_r = r
                while stack:
                    cr, cc = stack.pop()
                    component_cells.append((cr, cc))
                    min_r = min(min_r, cr)
                    max_r = max(max_r, cr)
                    for dr, dc in directions:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < height and 0 <= nc < width and not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                shape = []
                for cr, cc in component_cells:
                    offset = cr - min_r
                    shape.append((offset, cc))
                comp = {'min_r': min_r, 'height': max_r - min_r + 1, 'shape': shape, 'color': color}
                components.append(comp)

    if not components:
        return [row[:] for row in grid]

    components.sort(key=lambda x: x['min_r'])
    components = components[::-1]
    overall_start = min(comp['min_r'] for comp in components)
    output = [[0] * width for _ in range(height)]
    current_r = overall_start
    for comp in components:
        for offset, cc in comp['shape']:
            output[current_r + offset][cc] = comp['color']
        current_r += comp['height']
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
