"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 19bb5feb
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[39](id=39)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0039__19bb5feb
"""
from __future__ import annotations



import numpy as np

import numpy as np
from collections import defaultdict

def transform(grid_lst: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid_lst)
    rows, cols = grid.shape

    # Find purple bounds
    purple_rows = np.any(grid == 8, axis=1)
    min_r = np.where(purple_rows)[0][0]
    max_r = np.where(purple_rows)[0][-1]
    purple_cols = np.any(grid == 8, axis=0)
    min_c = np.where(purple_cols)[0][0]
    max_c = np.where(purple_cols)[0][-1]
    center_c = (min_c + max_c) / 2

    # Find blocks
    visited = np.zeros_like(grid, dtype=bool)
    blocks = []
    for r in range(rows):
        for c in range(cols):
            color = grid[r, c]
            if color != 0 and color != 8 and not visited[r, c]:
                component = []
                stack = [(r, c)]
                visited[r, c] = True
                while stack:
                    rr, cc = stack.pop()
                    component.append((rr, cc))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = rr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr, nc] and grid[nr, nc] == color:
                            visited[nr, nc] = True
                            stack.append((nr, nc))
                rs = [rr for rr, _ in component]
                cs = [cc for _, cc in component]
                block_min_r = min(rs)
                block_min_c = min(cs)
                block_center_c = (min(cs) + max(cs)) / 2
                blocks.append({'color': color, 'min_r': block_min_r, 'min_c': block_min_c, 'center_c': block_center_c})

    # Group by min_r
    groups = defaultdict(list)
    for b in blocks:
        groups[b['min_r']].append(b)

    # Sort group rows
    group_rows = sorted(groups.keys())

    # Assume exactly two groups
    top_min_r = group_rows[0]
    bottom_min_r = group_rows[1]

    top_blocks = sorted(groups[top_min_r], key=lambda b: b['min_c'])
    bottom_blocks = sorted(groups[bottom_min_r], key=lambda b: b['min_c'])

    # Fill top row
    top_row = [0, 0]
    if len(top_blocks) == 2:
        top_row[0] = top_blocks[0]['color']
        top_row[1] = top_blocks[1]['color']
    elif len(top_blocks) == 1:
        b = top_blocks[0]
        if b['center_c'] <= center_c:
            top_row[0] = b['color']
        else:
            top_row[1] = b['color']

    # Fill bottom row
    bottom_row = [0, 0]
    if len(bottom_blocks) == 2:
        bottom_row[0] = bottom_blocks[0]['color']
        bottom_row[1] = bottom_blocks[1]['color']
    elif len(bottom_blocks) == 1:
        b = bottom_blocks[0]
        if b['center_c'] <= center_c:
            bottom_row[0] = b['color']
        else:
            bottom_row[1] = b['color']

    return [top_row, bottom_row]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
