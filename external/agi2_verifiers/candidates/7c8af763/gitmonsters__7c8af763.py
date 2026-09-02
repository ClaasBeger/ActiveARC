"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 7c8af763
source: GitMonsters/SOLVED-562-verified
original_path: solves/7c8af763/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__7c8af763
"""
from __future__ import annotations



"""
Task 7c8af763: Grid divided into rectangular regions by lines of 5s (with colored
markers). Fill each region's 0-cells with the majority color found among the
non-5 markers on its surrounding grid lines.
"""
import json
from collections import Counter


def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    output = [row[:] for row in grid]

    # Grid-line rows/cols contain no 0s
    gl_rows = sorted(r for r in range(rows) if all(grid[r][c] != 0 for c in range(cols)))
    gl_cols = sorted(c for c in range(cols) if all(grid[r][c] != 0 for r in range(rows)))

    # Regions lie between consecutive grid-line rows.
    # Column boundaries include virtual edges (-1 and cols) for side regions.
    col_bounds = [-1] + gl_cols + [cols]

    for ri in range(len(gl_rows) - 1):
        r_start = gl_rows[ri] + 1
        r_end = gl_rows[ri + 1] - 1
        if r_start > r_end:
            continue

        for ci in range(len(col_bounds) - 1):
            c_start = col_bounds[ci] + 1
            c_end = col_bounds[ci + 1] - 1
            if c_start > c_end:
                continue

            # Collect non-5 markers on the four surrounding grid lines
            markers: list[int] = []

            top_r = gl_rows[ri]
            for c in range(c_start, c_end + 1):
                if grid[top_r][c] != 5:
                    markers.append(grid[top_r][c])

            bot_r = gl_rows[ri + 1]
            for c in range(c_start, c_end + 1):
                if grid[bot_r][c] != 5:
                    markers.append(grid[bot_r][c])

            left_c = col_bounds[ci]
            if 0 <= left_c < cols:
                for r in range(r_start, r_end + 1):
                    if grid[r][left_c] != 5:
                        markers.append(grid[r][left_c])

            right_c = col_bounds[ci + 1]
            if 0 <= right_c < cols:
                for r in range(r_start, r_end + 1):
                    if grid[r][right_c] != 5:
                        markers.append(grid[r][right_c])

            if not markers:
                continue

            fill_color = Counter(markers).most_common(1)[0][0]

            for r in range(r_start, r_end + 1):
                for c in range(c_start, c_end + 1):
                    if output[r][c] == 0:
                        output[r][c] = fill_color

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
