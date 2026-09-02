"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: df9fd884
source: GitMonsters/SOLVED-562-verified
original_path: solves/df9fd884/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__df9fd884
"""
from __future__ import annotations



def transform(input_grid):
    grid = [row[:] for row in input_grid]
    rows = len(grid)
    cols = len(grid[0])

    # Find connected components of 4s (two U-shaped containers)
    visited = [[False]*cols for _ in range(rows)]
    containers = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 4 and not visited[r][c]:
                component = []
                queue = [(r, c)]
                visited[r][c] = True
                while queue:
                    cr, cc = queue.pop(0)
                    component.append((cr, cc))
                    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nr, nc = cr+dr, cc+dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == 4:
                            visited[nr][nc] = True
                            queue.append((nr, nc))
                containers.append(component)

    # Compute bounding box and interior for each container
    container_info = []
    for comp in containers:
        min_r = min(r for r,c in comp)
        max_r = max(r for r,c in comp)
        min_c = min(c for r,c in comp)
        max_c = max(c for r,c in comp)
        comp_set = set(comp)
        interior = [(r,c) for r in range(min_r, max_r+1)
                     for c in range(min_c, max_c+1) if (r,c) not in comp_set]
        interior_cols = sorted(set(c for r,c in interior))
        container_info.append({
            'interior_cols': interior_cols,
            'min_r': min_r, 'max_r': max_r,
        })

    # Find the colored object (not background 7, not container 4)
    object_cells = []
    object_color = None
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 7 and grid[r][c] != 4:
                object_color = grid[r][c]
                object_cells.append((r, c))

    # Source container = the one whose interior cols contain the object's cols
    obj_cols = set(c for _,c in object_cells)
    source_idx = next(i for i, info in enumerate(container_info)
                      if obj_cols.issubset(set(info['interior_cols'])))
    dest_idx = 1 - source_idx
    source = container_info[source_idx]
    dest = container_info[dest_idx]

    # Map columns from source interior to destination interior
    col_map = dict(zip(source['interior_cols'], dest['interior_cols']))

    # Vertically align object with source container's grid edge
    obj_max_r = max(r for r,_ in object_cells)
    obj_min_r = min(r for r,_ in object_cells)
    if source['max_r'] > rows / 2:          # source at bottom → bottom-align
        row_shift = source['max_r'] - obj_max_r
    else:                                     # source at top → top-align
        row_shift = source['min_r'] - obj_min_r

    # Build output: remove object, place at new position
    output = [row[:] for row in grid]
    for r, c in object_cells:
        output[r][c] = 7
    for r, c in object_cells:
        output[r + row_shift][col_map[c]] = object_color
    return output


# ── Tests ──


# Catalog entry point: every solver in solves/ exposes solve(grid).
def solve(grid):
    return [list(row) for row in transform(grid)]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
