"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 84f2aca1
source: GitMonsters/SOLVED-562-verified
original_path: solves/84f2aca1/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__84f2aca1
"""
from __future__ import annotations



def solve(grid):
    """Find colored rectangles, fill interior: area=1 -> 5, area>=2 -> 7."""
    rows = len(grid)
    cols = len(grid[0])
    out = [row[:] for row in grid]
    visited = [[False] * cols for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                color = grid[r][c]
                stack = [(r, c)]
                cells = set()
                while stack:
                    cr, cc = stack.pop()
                    if (cr, cc) in cells:
                        continue
                    if 0 <= cr < rows and 0 <= cc < cols and grid[cr][cc] == color:
                        cells.add((cr, cc))
                        visited[cr][cc] = True
                        stack.extend([(cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)])

                min_r = min(x[0] for x in cells)
                max_r = max(x[0] for x in cells)
                min_c = min(x[1] for x in cells)
                max_c = max(x[1] for x in cells)

                interior = []
                for ir in range(min_r + 1, max_r):
                    for ic in range(min_c + 1, max_c):
                        if grid[ir][ic] == 0:
                            interior.append((ir, ic))

                if interior:
                    fill = 5 if len(interior) == 1 else 7
                    for ir, ic in interior:
                        out[ir][ic] = fill

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
