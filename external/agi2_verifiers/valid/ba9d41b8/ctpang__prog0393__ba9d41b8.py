"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ba9d41b8
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[393](id=393)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0393__ba9d41b8
"""
from __future__ import annotations



import numpy as np

from collections import deque

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    
    h = len(grid)
    w = len(grid[0])
    
    output = [row[:] for row in grid]
    visited = [[False] * w for _ in range(h)]
    
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for i in range(h):
        for j in range(w):
            if grid[i][j] > 0 and not visited[i][j]:
                color = grid[i][j]
                component = []
                q = deque([(i, j)])
                visited[i][j] = True
                while q:
                    x, y = q.popleft()
                    component.append((x, y))
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < h and 0 <= ny < w and not visited[nx][ny] and grid[nx][ny] == color:
                            visited[nx][ny] = True
                            q.append((nx, ny))
                
                if not component:
                    continue
                
                min_r = min(pos[0] for pos in component)
                max_r = max(pos[0] for pos in component)
                min_c = min(pos[1] for pos in component)
                max_c = max(pos[1] for pos in component)
                
                expected_size = (max_r - min_r + 1) * (max_c - min_c + 1)
                if len(component) != expected_size:
                    continue  # Not a solid rectangle
                
                hh = max_r - min_r + 1
                ww = max_c - min_c + 1
                
                for lr in range(1, hh - 1):
                    global_r = min_r + lr
                    if lr % 2 == 1:  # Type A
                        start, step = 1, 2
                    else:  # Type B
                        start, step = 2, 2
                    for lc in range(start, ww - 1, step):
                        global_c = min_c + lc
                        output[global_r][global_c] = 0
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
