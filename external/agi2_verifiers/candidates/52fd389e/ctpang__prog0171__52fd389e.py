"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 52fd389e
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[171](id=171)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0171__52fd389e
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    rows, cols = grid.shape
    visited = np.zeros((rows, cols), dtype=bool)
    
    def dfs(r, c, component):
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if cr < 0 or cr >= rows or cc < 0 or cc >= cols or visited[cr, cc] or grid[cr, cc] == 0:
                continue
            visited[cr, cc] = True
            component.append((cr, cc))
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                stack.append((cr + dr, cc + dc))
    
    components = []
    for r in range(rows):
        for c in range(cols):
            if grid[r, c] != 0 and not visited[r, c]:
                component = []
                dfs(r, c, component)
                components.append(component)
    
    for component in components:
        non_four_colors = set(grid[r, c] for r, c in component if grid[r, c] != 4)
        if len(non_four_colors) != 1:
            continue  # Assuming always one color, as per examples
        color = next(iter(non_four_colors))
        k = sum(1 for r, c in component if grid[r, c] == color)
        
        rs, cs = zip(*component)
        min_r, max_r = min(rs), max(rs)
        min_c, max_c = min(cs), max(cs)
        
        exp_min_r = max(0, min_r - k)
        exp_max_r = min(rows - 1, max_r + k)
        exp_min_c = max(0, min_c - k)
        exp_max_c = min(cols - 1, max_c + k)
        
        for er in range(exp_min_r, exp_max_r + 1):
            for ec in range(exp_min_c, exp_max_c + 1):
                if grid[er, ec] == 0:
                    grid[er, ec] = color
    
    return grid.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
