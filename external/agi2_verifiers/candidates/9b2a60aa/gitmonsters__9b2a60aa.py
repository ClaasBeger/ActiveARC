"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9b2a60aa
source: GitMonsters/SOLVED-562-verified
original_path: solves/9b2a60aa/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__9b2a60aa
"""
from __future__ import annotations



"""
ARC-AGI task 9b2a60aa solver.

Pattern: A template shape + a line of colored dots.
The dot matching the shape's color anchors the shape's position.
Each dot generates a copy of the shape in the dot's color.
Copies are spaced so that gaps between consecutive copies
equal gaps between consecutive dots.
"""
import json
import copy
from collections import deque
from typing import List

Grid = List[List[int]]


def solve(grid: Grid) -> Grid:
    rows = len(grid)
    cols = len(grid[0])

    # Collect non-zero cells
    nonzero = {}
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                nonzero[(r, c)] = grid[r][c]

    # 8-connected components via BFS
    visited = set()
    components = []
    for (r, c) in nonzero:
        if (r, c) in visited:
            continue
        comp = []
        queue = deque([(r, c)])
        visited.add((r, c))
        while queue:
            cr, cc = queue.popleft()
            comp.append((cr, cc, nonzero[(cr, cc)]))
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = cr + dr, cc + dc
                    if (nr, nc) in nonzero and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
        components.append(comp)

    # Largest component = shape; single-cell components = dots
    components.sort(key=len, reverse=True)
    shape = components[0]
    dots = [comp[0] for comp in components[1:] if len(comp) == 1]

    shape_color = shape[0][2]

    # Shape bounding box
    min_r = min(p[0] for p in shape)
    max_r = max(p[0] for p in shape)
    min_c = min(p[1] for p in shape)
    max_c = max(p[1] for p in shape)

    # Shape pixels relative to bounding-box top-left
    shape_pixels = [(p[0] - min_r, p[1] - min_c) for p in shape]

    # Determine dot axis: horizontal (same row) or vertical (same col)
    dot_rows = set(d[0] for d in dots)
    dot_cols = set(d[1] for d in dots)
    horizontal = len(dot_rows) < len(dot_cols)

    if horizontal:
        dots.sort(key=lambda d: d[1])
        dot_positions = [d[1] for d in dots]
        shape_par_start = min_c
        shape_size = max_c - min_c + 1
        shape_perp_start = min_r
    else:
        dots.sort(key=lambda d: d[0])
        dot_positions = [d[0] for d in dots]
        shape_par_start = min_r
        shape_size = max_r - min_r + 1
        shape_perp_start = min_c

    # Find anchor dot (same color as shape)
    anchor = next(i for i, d in enumerate(dots) if d[2] == shape_color)

    # Build output
    output = copy.deepcopy(grid)

    for i, dot in enumerate(dots):
        color = dot[2]
        par_start = (
            shape_par_start
            + (dot_positions[i] - dot_positions[anchor])
            + (i - anchor) * (shape_size - 1)
        )
        for dr, dc in shape_pixels:
            if horizontal:
                r, c = shape_perp_start + dr, par_start + dc
            else:
                r, c = par_start + dr, shape_perp_start + dc
            if 0 <= r < rows and 0 <= c < cols:
                output[r][c] = color

    return output


# ── Verification ──────────────────────────────────────────────────────

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
