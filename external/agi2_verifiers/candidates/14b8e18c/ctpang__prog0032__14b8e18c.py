"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 14b8e18c
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[32](id=32)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0032__14b8e18c
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    output = [row[:] for row in grid]
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 7 and not visited[r][c]:
                component = []
                stack = [(r, c)]
                visited[r][c] = True
                color = grid[r][c]
                while stack:
                    cr, cc = stack.pop()
                    component.append((cr, cc))
                    for dr, dc in directions:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            stack.append((nr, nc))

                # Check if all have exactly 2 neighbors
                is_cycle = True
                for cr, cc in component:
                    neigh_count = 0
                    for dr, dc in directions:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == color:
                            neigh_count += 1
                    if neigh_count != 2:
                        is_cycle = False
                        break

                if is_cycle:
                    # Process bends
                    for cr, cc in component:
                        neigh_dirs = []
                        for i, (dr, dc) in enumerate(directions):
                            nr, nc = cr + dr, cc + dc
                            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == color:
                                neigh_dirs.append(i)
                        # Should be exactly 2
                        if len(neigh_dirs) == 2:
                            i1, i2 = sorted(neigh_dirs)
                            # Not opposite
                            if not ((i1 == 0 and i2 == 1) or (i1 == 2 and i2 == 3)):
                                # Bend, find missing
                                all_dirs = {0, 1, 2, 3}
                                missing = all_dirs - set(neigh_dirs)
                                for mi in missing:
                                    dr, dc = directions[mi]
                                    nr, nc = cr + dr, cc + dc
                                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 7:
                                        output[nr][nc] = 2

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
