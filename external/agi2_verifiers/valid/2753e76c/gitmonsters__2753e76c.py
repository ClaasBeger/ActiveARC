"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 2753e76c
source: GitMonsters/SOLVED-562-verified
original_path: solves/2753e76c/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__2753e76c
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    rows, cols = len(grid), len(grid[0])
    visited = [[False] * cols for _ in range(rows)]

    color_counts: dict[int, int] = {}

    def flood_fill(r: int, c: int, color: int) -> None:
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if 0 <= cr < rows and 0 <= cc < cols and not visited[cr][cc] and grid[cr][cc] == color:
                visited[cr][cc] = True
                stack.extend([(cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)])

    # Count distinct connected rectangles per color
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                color = grid[r][c]
                flood_fill(r, c, color)
                color_counts[color] = color_counts.get(color, 0) + 1

    # Sort colors by rectangle count descending
    sorted_colors = sorted(color_counts.items(), key=lambda x: -x[1])

    n_colors = len(sorted_colors)
    max_count = sorted_colors[0][1] if sorted_colors else 0

    # Build staircase: each row right-filled with the color's count
    result = [[0] * max_count for _ in range(n_colors)]
    for i, (color, count) in enumerate(sorted_colors):
        for j in range(max_count - count, max_count):
            result[i][j] = color

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
