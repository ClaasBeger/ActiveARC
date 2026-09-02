"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e0fb7511
source: GitMonsters/SOLVED-562-verified
original_path: solves/e0fb7511/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__e0fb7511
"""
from __future__ import annotations



from collections import deque


def solve(grid):
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    out = [row[:] for row in grid]

    # Find connected components of 0s
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0 and not visited[r][c]:
                comp = []
                q = deque([(r, c)])
                visited[r][c] = True
                while q:
                    cr, cc = q.popleft()
                    comp.append((cr, cc))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == 0:
                            visited[nr][nc] = True
                            q.append((nr, nc))
                if len(comp) >= 2:
                    for cr, cc in comp:
                        out[cr][cc] = 8

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
