"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 72a961c9
source: GitMonsters/SOLVED-562-verified
original_path: solves/72a961c9/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__72a961c9
"""
from __future__ import annotations



from collections import Counter


def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    ARC puzzle 72a961c9.

    Rule: One row is a "key row" – it contains a horizontal sequence made
    mostly of a background color (1) with a few accent colors inserted.
    For each accent color v at column c, draw a vertical column of height h(v)
    going straight up from the key row:
      • The topmost cell gets the accent color v.
      • All cells between the tip and the key row get the background color.

    Height formula: h(v) = (number of unique accent colors strictly greater
    than v) + 3, with a +1 bonus when v is the sole accent color and equals
    background + 1.  This produces height 4 for the smallest accent and 3 for
    the largest, matching every training example.
    """
    result = [row[:] for row in grid]
    rows = len(grid)
    if not rows:
        return result
    cols = len(grid[0])

    # Key row = the row with the most non-zero values
    key_row_idx = max(range(rows), key=lambda r: sum(1 for v in grid[r] if v != 0))
    key_row = grid[key_row_idx]

    # Background = most frequent value in the key row
    bg = Counter(key_row).most_common(1)[0][0]

    # Unique accent (non-background) values
    accents = sorted({v for v in key_row if v != bg})
    if not accents:
        return result

    def height_for(v: int) -> int:
        count_greater = sum(1 for u in accents if u > v)
        # When v is the sole largest accent and sits one step above background,
        # it earns an extra unit of height (distinguishes single-2 from single-8).
        bonus = 1 if (count_greater == 0 and v - bg == 1) else 0
        return count_greater + 3 + bonus

    height_map = {v: height_for(v) for v in accents}

    # Draw a vertical column for every accent cell in the key row
    for c, v in enumerate(key_row):
        if v == bg:
            continue
        h = height_map[v]
        tip_row = max(0, key_row_idx - h)
        result[tip_row][c] = v
        for r in range(tip_row + 1, key_row_idx):
            result[r][c] = bg

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
