"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 84f2aca1
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[272](id=272)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0272__84f2aca1
"""
from __future__ import annotations



import numpy as np

from collections import deque

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid:
        return []
    rows = len(grid)
    cols = len(grid[0])
    output = [row[:] for row in grid]
    visited = [[False] * cols for _ in range(rows)]
    q = deque()
    # Add border 0's
    for r in range(rows):
        for c in range(cols):
            if (r == 0 or r == rows - 1 or c == 0 or c == cols - 1) and grid[r][c] == 0 and not visited[r][c]:
                visited[r][c] = True
                q.append((r, c))
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    # Flood external 0's
    while q:
        r, c = q.popleft()
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and not visited[nr][nc]:
                visited[nr][nc] = True
                q.append((nr, nc))
    # Find and fill internal components
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0 and not visited[r][c]:
                # New component
                component = []
                comp_q = deque()
                comp_q.append((r, c))
                visited[r][c] = True
                while comp_q:
                    cr, cc = comp_q.popleft()
                    component.append((cr, cc))
                    for dr, dc in dirs:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and not visited[nr][nc]:
                            visited[nr][nc] = True
                            comp_q.append((nr, nc))
                size = len(component)
                if size == 1:
                    fill_color = 5
                elif size == 2:
                    fill_color = 7
                else:
                    fill_color = 0  # Default, though not needed
                for pr, pc in component:
                    output[pr][pc] = fill_color
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
