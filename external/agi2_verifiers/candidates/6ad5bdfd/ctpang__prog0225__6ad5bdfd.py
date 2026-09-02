"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 6ad5bdfd
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[225](id=225)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0225__6ad5bdfd
"""
from __future__ import annotations



import numpy as np

import numpy as np

def find_component(grid, r, c, visited, height, width):
    color = grid[r, c]
    component = []
    stack = [(r, c)]
    while stack:
        rr, cc = stack.pop()
        if visited[rr, cc]:
            continue
        visited[rr, cc] = True
        component.append((rr, cc))
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = rr + dr, cc + dc
            if 0 <= nr < height and 0 <= nc < width and not visited[nr, nc] and grid[nr, nc] == color:
                stack.append((nr, nc))
    return component, color

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    height, width = grid.shape
    base_pos = np.argwhere(grid == 2)
    if len(base_pos) == 0:
        return grid.tolist()
    rows_base = base_pos[:, 0]
    cols_base = base_pos[:, 1]
    if np.all(cols_base == cols_base[0]):
        is_vertical = True
        base_coord = cols_base[0]
        axis = 'col'
        if base_coord == 0:
            dir = -1
        elif base_coord == width - 1:
            dir = 1
        else:
            dir = 0  # Unknown, but assume edge
    elif np.all(rows_base == rows_base[0]):
        is_vertical = False
        base_coord = rows_base[0]
        axis = 'row'
        if base_coord == 0:
            dir = -1
        elif base_coord == height - 1:
            dir = 1
        else:
            dir = 0
    else:
        return grid.tolist()  # Unknown

    visited = np.zeros_like(grid, dtype=bool)
    shapes = []
    for r in range(height):
        for c in range(width):
            if grid[r, c] > 0 and grid[r, c] != 2 and not visited[r, c]:
                pos, color = find_component(grid, r, c, visited, height, width)
                shapes.append({'color': color, 'pos': pos})

    for shape in shapes:
        pos = shape['pos']
        if axis == 'col':
            cols = [cc for _, cc in pos]
            min_c = min(cols)
            max_c = max(cols)
            if dir == 1:
                shape['dist'] = base_coord - max_c
            elif dir == -1:
                shape['dist'] = min_c - base_coord
            else:
                shape['dist'] = 0
            shape['tiebreaker'] = min([rr for rr, _ in pos])
        else:
            rows = [rr for rr, _ in pos]
            min_r = min(rows)
            max_r = max(rows)
            if dir == 1:
                shape['dist'] = base_coord - max_r
            elif dir == -1:
                shape['dist'] = min_r - base_coord
            else:
                shape['dist'] = 0
            shape['tiebreaker'] = min([cc for _, cc in pos])

    shapes.sort(key=lambda s: (s['dist'], s['tiebreaker']))

    output = np.zeros_like(grid)
    for rr, cc in base_pos:
        output[rr, cc] = 2

    for shape in shapes:
        pos = shape['pos']
        color = shape['color']
        if axis == 'col':
            current_coords = [cc for _, cc in pos]
            min_current = min(current_coords)
            if dir == 1:
                max_delta = (width - 1) - max(current_coords)
                for delta in range(max_delta, -1, -1):
                    new_pos = [(rr, cc + delta) for rr, cc in pos]
                    if all(0 <= nc < width and output[nr, nc] == 0 for nr, nc in new_pos):
                        chosen_delta = delta
                        break
                else:
                    chosen_delta = 0
            elif dir == -1:
                min_delta = -min_current
                for delta in range(min_delta, 1):
                    new_pos = [(rr, cc + delta) for rr, cc in pos]
                    if all(0 <= nc < width and output[nr, nc] == 0 for nr, nc in new_pos):
                        chosen_delta = delta
                        break
                else:
                    chosen_delta = 0
            else:
                chosen_delta = 0
            new_pos = [(rr, cc + chosen_delta) for rr, cc in pos]
        else:
            current_coords = [rr for rr, _ in pos]
            min_current = min(current_coords)
            if dir == 1:
                max_delta = (height - 1) - max(current_coords)
                for delta in range(max_delta, -1, -1):
                    new_pos = [(rr + delta, cc) for rr, cc in pos]
                    if all(0 <= nr < height and output[nr, nc] == 0 for nr, nc in new_pos):
                        chosen_delta = delta
                        break
                else:
                    chosen_delta = 0
            elif dir == -1:
                min_delta = -min_current
                for delta in range(min_delta, 1):
                    new_pos = [(rr + delta, cc) for rr, cc in pos]
                    if all(0 <= nr < height and output[nr, nc] == 0 for nr, nc in new_pos):
                        chosen_delta = delta
                        break
                else:
                    chosen_delta = 0
            else:
                chosen_delta = 0
            new_pos = [(rr + chosen_delta, cc) for rr, cc in pos]
        for rr, cc in new_pos:
            output[rr, cc] = color

    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
