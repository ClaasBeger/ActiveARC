"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9a4bb226
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[324](id=324)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0324__9a4bb226
"""
from __future__ import annotations



import numpy as np

from collections import defaultdict

def transform(grid_lst: list[list[int]]) -> list[list[int]]:
    grid = grid_lst
    height = len(grid)
    if height == 0:
        return []
    width = len(grid[0])

    visited = [[False] * width for _ in range(height)]
    components = []

    for r in range(height):
        for c in range(width):
            if grid[r][c] != 0 and not visited[r][c]:
                minr, maxr = r, r
                minc, maxc = c, c
                colors = set([grid[r][c]])
                stack = [(r, c)]
                visited[r][c] = True
                area = 1

                while stack:
                    cr, cc = stack.pop()
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < height and 0 <= nc < width and grid[nr][nc] != 0 and not visited[nr][nc]:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                            minr = min(minr, nr)
                            maxr = max(maxr, nr)
                            minc = min(minc, nc)
                            maxc = max(maxc, nc)
                            colors.add(grid[nr][nc])
                            area += 1

                components.append({
                    'minr': minr, 'maxr': maxr, 'minc': minc, 'maxc': maxc,
                    'num_distinct': len(colors), 'area': area
                })

    if not components:
        return []

    max_distinct = max(c['num_distinct'] for c in components)
    candidates = [c for c in components if c['num_distinct'] == max_distinct]

    if len(candidates) > 1:
        max_area = max(c['area'] for c in candidates)
        candidates = [c for c in candidates if c['area'] == max_area]

    if len(candidates) > 1:
        min_minr = min(c['minr'] for c in candidates)
        candidates = [c for c in candidates if c['minr'] == min_minr]

    if len(candidates) > 1:
        min_minc = min(c['minc'] for c in candidates)
        candidates = [c for c in candidates if c['minc'] == min_minc]

    selected = candidates[0]

    out = []
    for r in range(selected['minr'], selected['maxr'] + 1):
        row = []
        for c in range(selected['minc'], selected['maxc'] + 1):
            row.append(grid[r][c])
        out.append(row)

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
