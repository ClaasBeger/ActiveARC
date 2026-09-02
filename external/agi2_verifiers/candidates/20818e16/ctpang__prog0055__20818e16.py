"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 20818e16
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[55](id=55)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0055__20818e16
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    
    rows = len(grid)
    cols = len(grid[0])
    bg = grid[0][0]
    visited = [[False] * cols for _ in range(rows)]
    components = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != bg and not visited[i][j]:
                color = grid[i][j]
                stack = [(i, j)]
                visited[i][j] = True
                pos = [(i, j)]
                min_r, max_r = i, i
                min_c, max_c = j, j
                while stack:
                    r, c = stack.pop()
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                            pos.append((nr, nc))
                            min_r = min(min_r, nr)
                            max_r = max(max_r, nr)
                            min_c = min(min_c, nc)
                            max_c = max(max_c, nc)
                area = len(pos)
                h = max_r - min_r + 1 if pos else 0
                w = max_c - min_c + 1 if pos else 0
                components.append((area, h, w, color))
    
    components.sort(key=lambda x: x[0])
    
    if not components:
        return []
    
    max_h = max(comp[1] for comp in components)
    max_w = max(comp[2] for comp in components)
    output = [[0 for _ in range(max_w)] for _ in range(max_h)]
    
    current_h = 0
    current_w = 0
    for _, comp_h, comp_w, color in components:
        new_h = max(current_h, comp_h)
        new_w = max(current_w, comp_w)
        # Fill added rows
        for r in range(current_h, new_h):
            for c in range(current_w):
                output[r][c] = color
        # Fill added columns
        for r in range(new_h):
            for c in range(current_w, new_w):
                output[r][c] = color
        current_h = new_h
        current_w = new_w
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
