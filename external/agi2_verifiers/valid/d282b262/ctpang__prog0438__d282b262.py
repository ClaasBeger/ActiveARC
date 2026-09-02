"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: d282b262
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[438](id=438)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0438__d282b262
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    rows = len(grid)
    cols = len(grid[0])
    
    # Find connected components
    visited = set()
    components = []
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != 0 and (i, j) not in visited:
                comp_cells = []
                stack = [(i, j)]
                visited.add((i, j))
                minr, maxr, minc, maxc = i, i, j, j
                while stack:
                    r, c = stack.pop()
                    color = grid[r][c]
                    comp_cells.append((r, c, color))
                    minr = min(minr, r)
                    maxr = max(maxr, r)
                    minc = min(minc, c)
                    maxc = max(maxc, c)
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 0 and (nr, nc) not in visited:
                            visited.add((nr, nc))
                            stack.append((nr, nc))
                components.append({
                    'cells': comp_cells,
                    'min_r': minr,
                    'max_r': maxr,
                    'min_c': minc,
                    'max_c': maxc
                })
    
    n = len(components)
    if n == 0:
        return grid
    
    # Build graph for groups based on row overlap
    graph = [[] for _ in range(n)]
    for a in range(n):
        for b in range(a + 1, n):
            if max(components[a]['min_r'], components[b]['min_r']) <= min(components[a]['max_r'], components[b]['max_r']):
                graph[a].append(b)
                graph[b].append(a)
    
    # Find connected components (groups)
    group_visited = [False] * n
    groups = []
    for start in range(n):
        if not group_visited[start]:
            group = []
            stack = [start]
            group_visited[start] = True
            while stack:
                cur = stack.pop()
                group.append(cur)
                for nei in graph[cur]:
                    if not group_visited[nei]:
                        group_visited[nei] = True
                        stack.append(nei)
            groups.append(group)
    
    # Initialize output grid to all 0
    output_grid = [[0 for _ in range(cols)] for _ in range(rows)]
    
    # Process each group
    for group in groups:
        # Sort shapes by max_c descending
        sorted_shapes = sorted(group, key=lambda idx: components[idx]['max_c'], reverse=True)
        
        for shape_idx in sorted_shapes:
            comp = components[shape_idx]
            orig_right = comp['max_c']
            # Get unique rows for this shape
            shape_rows = set(r for r, c, _ in comp['cells'])
            max_right = 14
            for row in shape_rows:
                left_obstacle = cols
                for cc in range(cols):
                    if output_grid[row][cc] != 0:
                        left_obstacle = cc
                        break
                max_right_row = left_obstacle - 1 if left_obstacle < cols else 14
                max_right = min(max_right, max_right_row)
            s = max_right - orig_right
            if s < 0:
                s = 0
            # Place cells
            for r, c, color in comp['cells']:
                new_c = c + s
                output_grid[r][new_c] = color
    
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
