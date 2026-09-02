"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e69241bd
source: GitMonsters/SOLVED-562-verified
original_path: solves/e69241bd/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__e69241bd
"""
from __future__ import annotations



from collections import deque


def solve(grid):
    """BFS flood fill from each non-0, non-5 seed through 0 cells. 5s are walls."""
    rows = len(grid)
    cols = len(grid[0])
    out = [row[:] for row in grid]

    seeds = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] not in (0, 5):
                seeds.append((r, c, grid[r][c]))

    for sr, sc, color in seeds:
        q = deque([(sr, sc)])
        visited = {(sr, sc)}
        while q:
            r, c = q.popleft()
            out[r][c] = color
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                    if grid[nr][nc] == 0:
                        visited.add((nr, nc))
                        q.append((nr, nc))

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
