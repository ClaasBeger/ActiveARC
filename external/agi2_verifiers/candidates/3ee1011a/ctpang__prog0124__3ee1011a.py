"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 3ee1011a
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[124](id=124)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0124__3ee1011a
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    
    height = len(grid)
    width = len(grid[0])
    visited = [[False] * width for _ in range(height)]
    components = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for r in range(height):
        for c in range(width):
            if grid[r][c] > 0 and not visited[r][c]:
                color = grid[r][c]
                size = 0
                stack = [(r, c)]
                visited[r][c] = True
                while stack:
                    cr, cc = stack.pop()
                    size += 1
                    for dr, dc in directions:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < height and 0 <= nc < width and not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                components.append((size, color))
    
    if not components:
        return []
    
    components.sort(key=lambda x: -x[0])
    max_n = components[0][0]
    parity = max_n % 2
    output = [[0] * max_n for _ in range(max_n)]
    
    for L, c in components:
        eff_s = L if L % 2 == parity else L - 1
        start = (max_n - eff_s) // 2
        for i in range(start, start + eff_s):
            for j in range(start, start + eff_s):
                output[i][j] = c
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
