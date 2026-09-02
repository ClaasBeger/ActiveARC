"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e1baa8a4
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[474](id=474)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0474__e1baa8a4
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []

    rows = len(grid)
    cols = len(grid[0])

    def find_rectangles():
        visited = [[False] * cols for _ in range(rows)]
        rects = []
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] != 0 and not visited[r][c]:
                    color = grid[r][c]
                    # Extend right
                    c_right = c
                    while c_right + 1 < cols and grid[r][c_right + 1] == color and not visited[r][c_right + 1]:
                        c_right += 1
                    # Extend down
                    r_bottom = r
                    while True:
                        next_r = r_bottom + 1
                        if next_r >= rows:
                            break
                        good = True
                        for cc in range(c, c_right + 1):
                            if grid[next_r][cc] != color or visited[next_r][cc]:
                                good = False
                                break
                        if not good:
                            break
                        r_bottom = next_r
                    # Mark visited
                    for rr in range(r, r_bottom + 1):
                        for cc in range(c, c_right + 1):
                            visited[rr][cc] = True
                    # Add rect (min_r, max_r, min_c, max_c, color)
                    rects.append((r, r_bottom, c, c_right, color))
        return rects

    rects = find_rectangles()

    h_set = set()
    v_set = set()
    for min_r, max_r, min_c, max_c, _ in rects:
        h_set.add(min_r)
        h_set.add(max_r + 1)
        v_set.add(min_c)
        v_set.add(max_c + 1)

    h_lines = sorted(h_set)
    v_lines = sorted(v_set)

    num_log_rows = len(h_lines) - 1
    num_log_cols = len(v_lines) - 1

    if num_log_rows == 0 or num_log_cols == 0:
        return []

    output = [[0] * num_log_cols for _ in range(num_log_rows)]

    for i in range(num_log_rows):
        pixel_r = h_lines[i]
        for j in range(num_log_cols):
            pixel_c = v_lines[j]
            if 0 <= pixel_r < rows and 0 <= pixel_c < cols:
                output[i][j] = grid[pixel_r][pixel_c]

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
