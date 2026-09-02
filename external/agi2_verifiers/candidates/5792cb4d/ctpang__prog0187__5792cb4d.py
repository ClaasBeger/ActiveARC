"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 5792cb4d
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[187](id=187)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0187__5792cb4d
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []
    
    rows = len(grid)
    cols = len(grid[0])
    background = 8
    
    # Find all non-background cells
    component = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] != background]
    
    if not component:
        return [row[:] for row in grid]
    
    # Get neighbors function
    def get_neighbors(r, c):
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        res = []
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != background:
                res.append((nr, nc))
        return res
    
    # Compute degrees
    degrees = {p: len(get_neighbors(*p)) for p in component}
    
    # Find ends (degree 1)
    ends = [p for p in degrees if degrees[p] == 1]
    
    # Assume exactly two ends
    if len(ends) != 2:
        # If not a chain, return original (or handle differently, but per examples it's a chain)
        return [row[:] for row in grid]
    
    # Choose start: min by row, then col
    start = min(ends, key=lambda p: (p[0], p[1]))
    
    # Traverse the path
    path = []
    current = start
    visited = set()
    while True:
        path.append(current)
        visited.add(current)
        neigh = [n for n in get_neighbors(*current) if n not in visited]
        if not neigh:
            break
        # Assume no branches
        if len(neigh) != 1:
            # If branch, return original (but per examples no)
            return [row[:] for row in grid]
        current = neigh[0]
    
    # Check all visited
    if len(path) != len(component):
        return [row[:] for row in grid]
    
    # Collect colors
    colors = [grid[r][c] for r, c in path]
    
    # Reverse colors
    reversed_colors = colors[::-1]
    
    # Create output
    output = [row[:] for row in grid]
    for i, (r, c) in enumerate(path):
        output[r][c] = reversed_colors[i]
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
