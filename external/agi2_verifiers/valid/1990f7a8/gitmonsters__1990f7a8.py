"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 1990f7a8
source: GitMonsters/SOLVED-562-verified
original_path: solves/1990f7a8/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__1990f7a8
"""
from __future__ import annotations



from collections import deque


def solve(grid: list[list[int]]) -> list[list[int]]:
    """Extract four 3x3 clusters from the grid and arrange them in a 7x7 output
    based on their spatial positions (2x2 quadrant layout with separator)."""
    rows, cols = len(grid), len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    clusters: list[tuple[float, float, list[list[int]]]] = []

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                q = deque([(r, c)])
                visited[r][c] = True
                cells = []
                while q:
                    cr, cc = q.popleft()
                    cells.append((cr, cc))
                    for dr in range(-1, 2):
                        for dc in range(-1, 2):
                            nr, nc = cr + dr, cc + dc
                            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] != 0:
                                visited[nr][nc] = True
                                q.append((nr, nc))

                min_r = min(cr for cr, _ in cells)
                max_r = max(cr for cr, _ in cells)
                min_c = min(cc for _, cc in cells)
                max_c = max(cc for _, cc in cells)

                patch = [[0] * 3 for _ in range(3)]
                for cr, cc in cells:
                    patch[cr - min_r][cc - min_c] = grid[cr][cc]

                center_r = (min_r + max_r) / 2
                center_c = (min_c + max_c) / 2
                clusters.append((center_r, center_c, patch))

    # Sort into quadrants: top 2 vs bottom 2 by row, then left/right by col
    clusters.sort(key=lambda x: x[0])
    top = sorted(clusters[:2], key=lambda x: x[1])
    bottom = sorted(clusters[2:], key=lambda x: x[1])

    result = [[0] * 7 for _ in range(7)]
    quadrants = [(0, 0, top[0]), (0, 4, top[1]), (4, 0, bottom[0]), (4, 4, bottom[1])]
    for row_off, col_off, (_, _, patch) in quadrants:
        for r in range(3):
            for c in range(3):
                result[row_off + r][col_off + c] = patch[r][c]

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
