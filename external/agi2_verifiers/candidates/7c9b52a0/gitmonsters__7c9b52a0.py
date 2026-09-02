"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 7c9b52a0
source: GitMonsters/SOLVED-562-verified
original_path: solves/7c9b52a0/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__7c9b52a0
"""
from __future__ import annotations



"""
ARC-AGI Task 7c9b52a0 Solver

Pattern: Multiple same-sized rectangular patches (containing 0s and colored pixels)
sit on a uniform background. The output overlays all patches — each patch contributes
its non-zero cells to a single combined grid.
"""
import json
from collections import Counter, deque
from typing import List

Grid = List[List[int]]


def solve(grid: Grid) -> Grid:
    rows, cols = len(grid), len(grid[0])

    # Background = most frequent value
    bg = Counter(v for row in grid for v in row).most_common(1)[0][0]

    # BFS to find connected components of non-background cells
    visited = [[False] * cols for _ in range(rows)]
    components: list[list[tuple[int, int]]] = []

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != bg and not visited[r][c]:
                comp: list[tuple[int, int]] = []
                q = deque([(r, c)])
                visited[r][c] = True
                while q:
                    cr, cc = q.popleft()
                    comp.append((cr, cc))
                    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] != bg:
                            visited[nr][nc] = True
                            q.append((nr, nc))
                components.append(comp)

    # Extract each rectangle (bounding-box contents)
    rectangles: list[Grid] = []
    for comp in components:
        min_r = min(r for r, _ in comp)
        max_r = max(r for r, _ in comp)
        min_c = min(c for _, c in comp)
        max_c = max(c for _, c in comp)
        rect = [row[min_c:max_c + 1] for row in grid[min_r:max_r + 1]]
        rectangles.append(rect)

    # All rectangles share the same dimensions
    h, w = len(rectangles[0]), len(rectangles[0][0])

    # Overlay: 0 is the default, non-zero cells from any rectangle are placed on top
    output = [[0] * w for _ in range(h)]
    for rect in rectangles:
        for r in range(h):
            for c in range(w):
                if rect[r][c] != 0:
                    output[r][c] = rect[r][c]

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
