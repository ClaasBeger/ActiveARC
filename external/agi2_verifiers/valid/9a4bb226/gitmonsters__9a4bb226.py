"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9a4bb226
source: GitMonsters/SOLVED-562-verified
original_path: solves/9a4bb226/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__9a4bb226
"""
from __future__ import annotations



def solve(grid):
    """Find the 3x3 block with the most distinct colors."""
    rows = len(grid)
    cols = len(grid[0])

    blocks = []
    visited = [[False] * cols for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                stack = [(r, c)]
                cells = []
                while stack:
                    cr, cc = stack.pop()
                    if 0 <= cr < rows and 0 <= cc < cols and not visited[cr][cc] and grid[cr][cc] != 0:
                        visited[cr][cc] = True
                        cells.append((cr, cc))
                        stack.extend([(cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)])
                if cells:
                    min_r = min(x[0] for x in cells)
                    min_c = min(x[1] for x in cells)
                    max_r = max(x[0] for x in cells)
                    max_c = max(x[1] for x in cells)
                    block = []
                    for br in range(min_r, max_r + 1):
                        block.append([grid[br][bc] for bc in range(min_c, max_c + 1)])
                    colors = set()
                    for row in block:
                        for v in row:
                            if v != 0:
                                colors.add(v)
                    blocks.append((len(colors), block))

    blocks.sort(key=lambda x: x[0], reverse=True)
    return blocks[0][1]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
