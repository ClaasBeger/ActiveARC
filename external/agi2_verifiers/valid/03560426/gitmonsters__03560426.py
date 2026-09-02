"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 03560426
source: GitMonsters/SOLVED-562-verified
original_path: solves/03560426/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__03560426
"""
from __future__ import annotations



import json, sys

def solve(grid):
    rows = len(grid)
    cols = len(grid[0])

    # Find connected blocks of same non-zero color
    visited = [[False] * cols for _ in range(rows)]
    blocks = []

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                color = grid[r][c]
                queue = [(r, c)]
                visited[r][c] = True
                cells = [(r, c)]
                while queue:
                    cr, cc = queue.pop(0)
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            queue.append((nr, nc))
                            cells.append((nr, nc))
                min_r = min(x[0] for x in cells)
                max_r = max(x[0] for x in cells)
                min_c = min(x[1] for x in cells)
                max_c = max(x[1] for x in cells)
                blocks.append((min_c, min_r, color, max_r - min_r + 1, max_c - min_c + 1))

    blocks.sort()

    result = [[0] * cols for _ in range(rows)]
    start_r, start_c = 0, 0
    for _, _, color, h, w in blocks:
        for dr in range(h):
            for dc in range(w):
                nr, nc = start_r + dr, start_c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    result[nr][nc] = color
        start_r += h - 1
        start_c += w - 1

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
