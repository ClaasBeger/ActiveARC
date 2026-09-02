"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: b457fec5
source: GitMonsters/SOLVED-562-verified
original_path: solves/b457fec5/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__b457fec5
"""
from __future__ import annotations



import json
from collections import deque


def solve(grid):
    rows = len(grid)
    cols = len(grid[0])
    output = [row[:] for row in grid]

    # Find color key: non-zero, non-5 cells in one row
    key_cells = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and grid[r][c] != 5:
                key_cells.append((r, c, grid[r][c]))

    # Group by row and extract sequence
    color_rows: dict[int, list] = {}
    for r, c, v in key_cells:
        color_rows.setdefault(r, []).append((c, v))

    color_seq = []
    for r in sorted(color_rows):
        cells = sorted(color_rows[r])
        color_seq = [v for _, v in cells]
        break

    n = len(color_seq)

    # Find connected components of 5s
    visited = [[False] * cols for _ in range(rows)]
    shapes = []

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 5 and not visited[r][c]:
                component = []
                queue = deque([(r, c)])
                visited[r][c] = True
                while queue:
                    cr, cc = queue.popleft()
                    component.append((cr, cc))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == 5:
                            visited[nr][nc] = True
                            queue.append((nr, nc))
                shapes.append(component)

    # Process each shape
    for shape in shapes:
        row_cells: dict[int, list] = {}
        for r, c in shape:
            row_cells.setdefault(r, []).append(c)

        shape_rows = sorted(row_cells.keys())
        left_edges = {}
        right_edges = {}
        widths = {}

        for r in shape_rows:
            cells = sorted(row_cells[r])
            left_edges[r] = cells[0]
            right_edges[r] = cells[-1]
            widths[r] = cells[-1] - cells[0] + 1

        min_width = min(widths.values())
        first_row = shape_rows[0]

        right_advance = max(right_edges.values()) - right_edges[first_row]
        left_advance = left_edges[first_row] - min(left_edges.values())

        if right_advance >= left_advance:
            # Right-expanding: fill from right edge inward
            first_right = right_edges[first_row]
            for r in shape_rows:
                right = right_edges[r]
                left = left_edges[r]
                base_idx = (right - first_right) % n
                for c in range(left, right + 1):
                    p = right - c  # position from right edge (0 = rightmost)
                    if p < min_width:
                        output[r][c] = color_seq[base_idx]
                    else:
                        k = p - min_width + 1
                        output[r][c] = color_seq[(base_idx - k) % n]
        else:
            # Left-expanding: fill from left edge inward
            first_left = left_edges[first_row]
            for r in shape_rows:
                right = right_edges[r]
                left = left_edges[r]
                base_idx = (first_left - left) % n
                for c in range(left, right + 1):
                    p = c - left  # position from left edge (0 = leftmost)
                    if p < min_width:
                        output[r][c] = color_seq[base_idx]
                    else:
                        k = p - min_width + 1
                        output[r][c] = color_seq[(base_idx - k) % n]

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
