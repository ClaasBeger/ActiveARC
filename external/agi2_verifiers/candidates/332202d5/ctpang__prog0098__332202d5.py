"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 332202d5
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[98](id=98)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0098__332202d5
"""
from __future__ import annotations



import numpy as np

import numpy as np
from collections import defaultdict

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    rows, cols = grid.shape

    # Find vertical_col: the column with the most 1s
    col_counts = defaultdict(int)
    for c in range(cols):
        for r in range(rows):
            if grid[r, c] == 1:
                col_counts[c] += 1
    vertical_col = max(col_counts, key=col_counts.get)

    # Find bars: list of (row, color)
    bars = []
    for r in range(rows):
        if grid[r, vertical_col] == 1:
            # Find candidate color (use first non-vertical col)
            cand_col = 0 if vertical_col != 0 else 1
            c = grid[r, cand_col]
            is_bar = True
            for cc in range(cols):
                if cc == vertical_col:
                    if grid[r, cc] != 1:
                        is_bar = False
                        break
                else:
                    if grid[r, cc] != c:
                        is_bar = False
                        break
            if is_bar:
                bars.append((r, c))
    bars.sort()  # sort by row

    # Find separator rows
    separator_rows = set()
    for i in range(len(bars) - 1):
        r1, c1 = bars[i]
        r2, c2 = bars[i + 1]
        if c1 != c2 and (r1 + r2) % 2 == 0:
            mid = (r1 + r2) // 2
            if r1 < mid < r2:
                separator_rows.add(mid)

    # Original rows
    original_rows = set(r for r, c in bars)

    # Create output
    output = np.zeros((rows, cols), dtype=int)
    for r in range(rows):
        if r in original_rows:
            output[r] = 1
            output[r, vertical_col] = 8
        elif r in separator_rows:
            output[r] = 1
        else:
            # Find nearest bar
            min_dist = float('inf')
            nearest_color = 0
            for bar_r, bar_c in bars:
                dist = abs(r - bar_r)
                if dist < min_dist:
                    min_dist = dist
                    nearest_color = bar_c
                elif dist == min_dist:
                    # If tie, colors should be the same, but set to this if different (shouldn't happen)
                    nearest_color = bar_c
            output[r] = nearest_color
            output[r, vertical_col] = 1

    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
