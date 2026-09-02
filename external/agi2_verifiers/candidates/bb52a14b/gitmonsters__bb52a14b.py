"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: bb52a14b
source: GitMonsters/SOLVED-562-verified
original_path: solves/bb52a14b/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__bb52a14b
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    grid = [row[:] for row in grid]
    rows, cols = len(grid), len(grid[0])

    # Find bounding box of all 4-valued cells (the template)
    fours = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 4]
    if not fours:
        return grid

    min_r = min(r for r, c in fours)
    max_r = max(r for r, c in fours)
    min_c = min(c for r, c in fours)
    max_c = max(c for r, c in fours)
    th = max_r - min_r + 1
    tw = max_c - min_c + 1

    template = [grid[r][min_c:max_c + 1] for r in range(min_r, max_r + 1)]

    # Scan for matching regions: non-4 cells must match, 4-cells must be 0
    for r in range(rows - th + 1):
        for c in range(cols - tw + 1):
            if r == min_r and c == min_c:
                continue
            match = True
            for dr in range(th):
                for dc in range(tw):
                    tv = template[dr][dc]
                    gv = grid[r + dr][c + dc]
                    if tv == 4:
                        if gv != 0:
                            match = False
                            break
                    else:
                        if gv != tv:
                            match = False
                            break
                if not match:
                    break
            if match:
                for dr in range(th):
                    for dc in range(tw):
                        if template[dr][dc] == 4:
                            grid[r + dr][c + dc] = 4

    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
