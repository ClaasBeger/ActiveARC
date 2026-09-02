"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: cfb2ce5a
source: GitMonsters/SOLVED-562-verified
original_path: solves/cfb2ce5a/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__cfb2ce5a
"""
from __future__ import annotations



"""Solver for ARC task cfb2ce5a.

Rule: A solid rectangular pattern block (2 colors) sits in the top-left area.
Colored marker cells outside the block encode color mappings for three reflected
copies that fill the remaining quadrants:
  - NE (right): horizontal flip of pattern
  - SW (below): vertical flip of pattern
  - SE (diagonal): 180-degree rotation of pattern
Each marker's position within its quadrant tells us which original color it
replaces (by looking up the flipped pattern at that relative position).
"""

from typing import List, Dict, Tuple


def solve(grid: List[List[int]]) -> List[List[int]]:
    rows = len(grid)
    cols = len(grid[0])
    result = [row[:] for row in grid]

    # Find top-left corner of pattern (first non-zero cell)
    r0, c0 = 0, 0
    for r in range(rows):
        found = False
        for c in range(cols):
            if grid[r][c] != 0:
                r0, c0 = r, c
                found = True
                break
        if found:
            break

    # Find pattern height (scan down first column)
    H = 0
    for r in range(r0, rows):
        if grid[r][c0] != 0:
            H += 1
        else:
            break

    # Find pattern width (each column must be fully non-zero within pattern rows)
    W = 0
    for c in range(c0, cols):
        if all(grid[r][c] != 0 for r in range(r0, r0 + H)):
            W += 1
        else:
            break

    # Extract pattern
    pattern = [
        [grid[r0 + i][c0 + j] for j in range(W)]
        for i in range(H)
    ]

    # Find markers (non-zero cells outside the pattern block)
    markers: List[Tuple[int, int, int]] = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                if not (r0 <= r < r0 + H and c0 <= c < c0 + W):
                    markers.append((r, c, grid[r][c]))

    # Build color maps for each quadrant from marker positions
    ne_map: Dict[int, int] = {}
    sw_map: Dict[int, int] = {}
    se_map: Dict[int, int] = {}

    for r, c, color in markers:
        if r0 <= r < r0 + H and c >= c0 + W:
            # NE quadrant — horizontal flip
            ri, ci = r - r0, c - (c0 + W)
            orig_color = pattern[ri][W - 1 - ci]
            ne_map[orig_color] = color
        elif r >= r0 + H and c0 <= c < c0 + W:
            # SW quadrant — vertical flip
            ri, ci = r - (r0 + H), c - c0
            orig_color = pattern[H - 1 - ri][ci]
            sw_map[orig_color] = color
        elif r >= r0 + H and c >= c0 + W:
            # SE quadrant — 180-degree rotation
            ri, ci = r - (r0 + H), c - (c0 + W)
            orig_color = pattern[H - 1 - ri][W - 1 - ci]
            se_map[orig_color] = color

    # Fill the three quadrants
    for i in range(H):
        for j in range(W):
            # NE: horizontal flip
            orig = pattern[i][W - 1 - j]
            result[r0 + i][c0 + W + j] = ne_map.get(orig, 0)

            # SW: vertical flip
            orig = pattern[H - 1 - i][j]
            result[r0 + H + i][c0 + j] = sw_map.get(orig, 0)

            # SE: 180-degree rotation
            orig = pattern[H - 1 - i][W - 1 - j]
            result[r0 + H + i][c0 + W + j] = se_map.get(orig, 0)

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
