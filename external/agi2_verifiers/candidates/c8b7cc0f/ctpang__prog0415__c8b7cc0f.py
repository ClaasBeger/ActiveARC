"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: c8b7cc0f
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[415](id=415)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0415__c8b7cc0f
"""
from __future__ import annotations



import numpy as np

from collections import deque

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    # Find noise color
    colors = set()
    for row in grid:
        for cell in row:
            colors.add(cell)
    colors.discard(0)
    colors.discard(1)
    if len(colors) != 1:
        raise ValueError("Expected exactly one noise color")
    noise_color = colors.pop()
    
    height = len(grid)
    width = len(grid[0])
    visited = set()
    queue = deque()
    
    # Add all border non-1 cells
    for r in range(height):
        for c in [0, width - 1]:
            if grid[r][c] != 1:
                if (r, c) not in visited:
                    visited.add((r, c))
                    queue.append((r, c))
    for c in range(width):
        for r in [0, height - 1]:
            if grid[r][c] != 1:
                if (r, c) not in visited:
                    visited.add((r, c))
                    queue.append((r, c))
    
    # Flood fill
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    while queue:
        x, y = queue.popleft()
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < height and 0 <= ny < width and (nx, ny) not in visited and grid[nx][ny] != 1:
                visited.add((nx, ny))
                queue.append((nx, ny))
    
    # Count inside noise cells
    count = 0
    for r in range(height):
        for c in range(width):
            if grid[r][c] == noise_color and (r, c) not in visited:
                count += 1
    
    # Create 3x3 output
    output = [[0] * 3 for _ in range(3)]
    idx = 0
    for r in range(3):
        for c in range(3):
            if idx < count:
                output[r][c] = noise_color
                idx += 1
            else:
                break
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
