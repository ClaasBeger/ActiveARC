"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 84db8fc4
source: GitMonsters/SOLVED-562-verified
original_path: solves/84db8fc4/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__84db8fc4
"""
from __future__ import annotations



def solve(grid):
    """Flood fill: boundary-reachable 0s become 2, interior 0s become 5."""
    rows = len(grid)
    cols = len(grid[0])
    out = [row[:] for row in grid]

    reachable = [[False] * cols for _ in range(rows)]
    stack = []

    for r in range(rows):
        for c in range(cols):
            if (r == 0 or r == rows - 1 or c == 0 or c == cols - 1) and grid[r][c] == 0:
                stack.append((r, c))

    while stack:
        r, c = stack.pop()
        if r < 0 or r >= rows or c < 0 or c >= cols:
            continue
        if reachable[r][c] or grid[r][c] != 0:
            continue
        reachable[r][c] = True
        stack.extend([(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)])

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                out[r][c] = 2 if reachable[r][c] else 5

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
