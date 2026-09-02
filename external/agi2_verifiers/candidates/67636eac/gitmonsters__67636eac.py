"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 67636eac
source: GitMonsters/SOLVED-562-verified
original_path: solves/67636eac/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__67636eac
"""
from __future__ import annotations



"""
ARC-AGI Puzzle 67636eac Solver

Pattern: Multiple same-sized shapes (each a unique non-zero color) are scattered
across the grid. Extract each shape's bounding box, then:
- If shapes are spread more horizontally → concatenate left-to-right (sorted by column)
- If shapes are spread more vertically → concatenate top-to-bottom (sorted by row)
"""
import json
import numpy as np


def solve(grid: list[list[int]]) -> list[list[int]]:
    g = np.array(grid)
    colors = sorted(set(g.flatten()) - {0})

    shapes = []
    for color in colors:
        positions = np.argwhere(g == color)
        min_r, min_c = positions.min(axis=0)
        max_r, max_c = positions.max(axis=0)

        bbox = g[min_r:max_r + 1, min_c:max_c + 1].copy()
        # Zero out any foreign colors in the bbox (safety for overlapping boxes)
        bbox[(bbox != color) & (bbox != 0)] = 0

        center_r = (min_r + max_r) / 2.0
        center_c = (min_c + max_c) / 2.0
        shapes.append((center_r, center_c, bbox))

    centers_r = [s[0] for s in shapes]
    centers_c = [s[1] for s in shapes]
    row_spread = max(centers_r) - min(centers_r)
    col_spread = max(centers_c) - min(centers_c)

    if col_spread >= row_spread:
        # Horizontal: sort by column, stack left-to-right
        shapes.sort(key=lambda s: s[1])
        result = np.hstack([s[2] for s in shapes])
    else:
        # Vertical: sort by row, stack top-to-bottom
        shapes.sort(key=lambda s: s[0])
        result = np.vstack([s[2] for s in shapes])

    return result.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
