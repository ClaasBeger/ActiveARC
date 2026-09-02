"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 070dd51e
source: GitMonsters/SOLVED-562-verified
original_path: solves/070dd51e/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__070dd51e
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """Find pairs of same-colored dots. Same-row pairs draw horizontal bars,
    same-column pairs draw vertical bars. Vertical bars take precedence at intersections."""
    rows = len(grid)
    cols = len(grid[0])
    output = [[0]*cols for _ in range(rows)]

    from collections import defaultdict
    dots: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                dots[grid[r][c]].append((r, c))

    h_lines = []
    v_lines = []

    for color, positions in dots.items():
        (r1, c1), (r2, c2) = positions
        if r1 == r2:
            h_lines.append((r1, min(c1, c2), max(c1, c2), color))
        else:
            v_lines.append((c1, min(r1, r2), max(r1, r2), color))

    for row, c1, c2, color in h_lines:
        for c in range(c1, c2 + 1):
            output[row][c] = color

    for col, r1, r2, color in v_lines:
        for r in range(r1, r2 + 1):
            output[r][col] = color

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
