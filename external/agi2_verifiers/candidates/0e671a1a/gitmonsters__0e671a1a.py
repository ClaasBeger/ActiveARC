"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 0e671a1a
source: GitMonsters/SOLVED-562-verified
original_path: solves/0e671a1a/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__0e671a1a
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    import copy
    result = copy.deepcopy(grid)
    rows, cols = len(grid), len(grid[0])

    # Find positions of 2, 3, 4
    pos = {}
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] in (2, 3, 4):
                pos[grid[r][c]] = (r, c)

    r2, c2 = pos[2]
    r3, c3 = pos[3]
    r4, c4 = pos[4]

    def fill_line(ra, ca, rb, cb):
        """Fill a horizontal or vertical line with 5s, not overwriting 2/3/4."""
        if ra == rb:  # horizontal
            for c in range(min(ca, cb), max(ca, cb) + 1):
                if result[ra][c] == 0:
                    result[ra][c] = 5
        else:  # vertical
            for r in range(min(ra, rb), max(ra, rb) + 1):
                if result[r][ca] == 0:
                    result[r][ca] = 5

    # L from 2 to 4: corner at (row_2, col_4)
    fill_line(r2, c2, r2, c4)  # horizontal segment
    fill_line(r2, c4, r4, c4)  # vertical segment

    # L from 4 to 3: corner at (row_4, col_3)
    fill_line(r4, c4, r4, c3)  # horizontal segment
    fill_line(r4, c3, r3, c3)  # vertical segment

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
