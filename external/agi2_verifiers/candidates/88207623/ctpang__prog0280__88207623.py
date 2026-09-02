"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 88207623
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[280](id=280)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0280__88207623
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    rows, cols = grid.shape
    visited = np.zeros_like(grid, dtype=bool)
    spines = []
    for i in range(rows):
        for j in range(cols):
            if grid[i, j] == 2 and not visited[i, j]:
                spine_rows = []
                col = j
                current_i = i
                # Collect upwards
                while current_i >= 0 and grid[current_i, col] == 2 and not visited[current_i, col]:
                    visited[current_i, col] = True
                    spine_rows.append(current_i)
                    current_i -= 1
                # Reset to after the upwards
                current_i = i + 1
                # Collect downwards
                while current_i < rows and grid[current_i, col] == 2 and not visited[current_i, col]:
                    visited[current_i, col] = True
                    spine_rows.append(current_i)
                    current_i += 1
                spine_rows = sorted(spine_rows)
                spines.append((col, min(spine_rows), max(spine_rows)))

    output = grid.copy()
    for axis_col, min_r, max_r in spines:
        seed_color = None
        seed_side = None
        seed_count = 0
        seed_pos = None
        for r in range(min_r, max_r + 1):
            for j in range(cols):
                if j == axis_col:
                    continue
                c = grid[r, j]
                if c != 0 and c != 2 and c != 4:
                    seed_color = c
                    seed_side = 'right' if j > axis_col else 'left'
                    seed_count += 1
                    seed_pos = (r, j)
        if seed_count != 1:
            continue
        body_side = 'left' if seed_side == 'right' else 'right'
        body_cond = lambda k: k < axis_col if body_side == 'left' else k > axis_col
        for r in range(min_r, max_r + 1):
            for j in range(cols):
                if grid[r, j] == 4 and body_cond(j):
                    j_mirror = 2 * axis_col - j
                    if 0 <= j_mirror < cols and output[r, j_mirror] == 0:
                        output[r, j_mirror] = seed_color

    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
