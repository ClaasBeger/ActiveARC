"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 93b4f4b3
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[305](id=305)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0305__93b4f4b3
"""
from __future__ import annotations



import numpy as np

import numpy as np

def find_components(grid, target):
    rows, cols = grid.shape
    visited = np.zeros((rows, cols), bool)
    components = []
    for i in range(rows):
        for j in range(cols):
            if grid[i, j] == target and not visited[i, j]:
                comp = []
                stack = [(i, j)]
                visited[i, j] = True
                while stack:
                    r, c = stack.pop()
                    comp.append((r, c))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr, nc] and grid[nr, nc] == target:
                            visited[nr, nc] = True
                            stack.append((nr, nc))
                components.append(comp)
    return components

def find_colored_components(grid):
    rows, cols = grid.shape
    visited = np.zeros((rows, cols), bool)
    components = []
    for i in range(rows):
        for j in range(cols):
            if grid[i, j] != 0 and not visited[i, j]:
                color = grid[i, j]
                comp = []
                stack = [(i, j)]
                visited[i, j] = True
                while stack:
                    r, c = stack.pop()
                    comp.append((r, c))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr, nc] and grid[nr, nc] == color:
                            visited[nr, nc] = True
                            stack.append((nr, nc))
                components.append((color, comp))
    return components

def normalize(pos):
    if not pos:
        return frozenset()
    min_r = min(r for r, _ in pos)
    min_c = min(c for _, c in pos)
    return frozenset((r - min_r, c - min_c) for r, c in pos)

def transform(grid_lst: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid_lst)
    rows, cols = grid.shape
    half = cols // 2
    left = grid[:, :half]
    right = grid[:, half:]
    holes = find_components(left, 0)
    colored_comps = find_colored_components(right)
    output = left.copy()
    for hole_pos in holes:
        shape = normalize(hole_pos)
        for col, comp_pos in colored_comps:
            if normalize(comp_pos) == shape:
                for r, c in hole_pos:
                    output[r, c] = col
                break
    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
