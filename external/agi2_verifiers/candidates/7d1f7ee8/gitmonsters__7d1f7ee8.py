"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 7d1f7ee8
source: GitMonsters/SOLVED-562-verified
original_path: solves/7d1f7ee8/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__7d1f7ee8
"""
from __future__ import annotations



"""
ARC-AGI Task 7d1f7ee8 Solver

Pattern: The grid contains nested hollow rectangles. Every non-zero cell
inside a hollow rectangle's interior gets recolored to the color of the
outermost enclosing rectangle.
"""

import json
from collections import deque
from typing import List


def solve(grid: List[List[int]]) -> List[List[int]]:
    rows = len(grid)
    cols = len(grid[0])
    output = [row[:] for row in grid]

    # Find connected components of non-zero colors via BFS
    visited = [[False] * cols for _ in range(rows)]
    components = []

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                color = grid[r][c]
                comp = []
                queue = deque([(r, c)])
                visited[r][c] = True
                while queue:
                    cr, cc = queue.popleft()
                    comp.append((cr, cc))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            queue.append((nr, nc))
                components.append((color, comp))

    # Identify which components form hollow rectangles
    rectangles = []
    for color, comp in components:
        min_r = min(r for r, c in comp)
        max_r = max(r for r, c in comp)
        min_c = min(c for r, c in comp)
        max_c = max(c for r, c in comp)

        # Need at least 3x3 to be hollow
        if max_r - min_r < 2 or max_c - min_c < 2:
            continue

        # Build expected border cell set
        expected = set()
        for cc in range(min_c, max_c + 1):
            expected.add((min_r, cc))
            expected.add((max_r, cc))
        for rr in range(min_r + 1, max_r):
            expected.add((rr, min_c))
            expected.add((rr, max_c))

        if set(comp) == expected:
            rectangles.append((color, min_r, max_r, min_c, max_c))

    # Sort by area descending so outermost rectangle is checked first
    rectangles.sort(key=lambda x: (x[2] - x[1]) * (x[4] - x[3]), reverse=True)

    # Replace each non-zero cell with the color of its outermost enclosing rectangle
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                for color, min_r, max_r, min_c, max_c in rectangles:
                    if min_r < r < max_r and min_c < c < max_c:
                        output[r][c] = color
                        break

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
