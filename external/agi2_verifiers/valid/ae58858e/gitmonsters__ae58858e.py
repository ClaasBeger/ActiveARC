"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ae58858e
source: GitMonsters/SOLVED-562-verified
original_path: solves/ae58858e/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__ae58858e
"""
from __future__ import annotations



def solve(grid):
    """Recolor connected components of color 2 with size >= 4 to color 6."""
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    result = [row[:] for row in grid]

    def bfs(sr, sc):
        from collections import deque
        q = deque([(sr, sc)])
        visited[sr][sc] = True
        cells = [(sr, sc)]
        while q:
            r, c = q.popleft()
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == 2:
                    visited[nr][nc] = True
                    q.append((nr, nc))
                    cells.append((nr, nc))
        return cells

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2 and not visited[r][c]:
                component = bfs(r, c)
                if len(component) >= 4:
                    for cr, cc in component:
                        result[cr][cc] = 6

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
