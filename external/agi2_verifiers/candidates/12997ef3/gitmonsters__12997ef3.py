"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 12997ef3
source: GitMonsters/SOLVED-562-verified
original_path: solves/12997ef3/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__12997ef3
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])

    # Extract template shape from cells with value 1
    ones = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 1]
    min_r = min(r for r, c in ones)
    max_r = max(r for r, c in ones)
    min_c = min(c for r, c in ones)
    max_c = max(c for r, c in ones)

    template = []
    for r in range(min_r, max_r + 1):
        row = []
        for c in range(min_c, max_c + 1):
            row.append(1 if grid[r][c] == 1 else 0)
        template.append(row)

    th = len(template)
    tw = len(template[0])

    # Find color markers (non-0, non-1 cells)
    colors = [(r, c, grid[r][c]) for r in range(rows) for c in range(cols) if grid[r][c] not in (0, 1)]

    # Determine tiling orientation from color marker layout
    if len(set(r for r, c, v in colors)) == 1:
        # Horizontal: all colors on same row → tile template side-by-side
        colors.sort(key=lambda x: x[1])
        result = []
        for tr in range(th):
            row = []
            for _, _, color in colors:
                for tc in range(tw):
                    row.append(color if template[tr][tc] == 1 else 0)
            result.append(row)
        return result
    else:
        # Vertical: all colors in same column → stack template copies
        colors.sort(key=lambda x: x[0])
        result = []
        for _, _, color in colors:
            for tr in range(th):
                row = []
                for tc in range(tw):
                    row.append(color if template[tr][tc] == 1 else 0)
                result.append(row)
        return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
