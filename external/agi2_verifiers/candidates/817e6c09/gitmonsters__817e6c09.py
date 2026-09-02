"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 817e6c09
source: GitMonsters/SOLVED-562-verified
original_path: solves/817e6c09/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__817e6c09
"""
from __future__ import annotations



"""
Task 817e6c09: Alternating 2x2 block recoloring.

The input contains 2×2 blocks of color 2 on a black (0) background.
Sort the blocks by their left-column position. Starting from the rightmost
block, alternate coloring: even index from the right → 8, odd → stays 2.
"""
from typing import List, Tuple


def _find_blocks(grid: List[List[int]]) -> List[Tuple[int, int]]:
    """Return top-left corners of all 2×2 blocks of value 2."""
    rows, cols = len(grid), len(grid[0])
    visited: set = set()
    blocks: List[Tuple[int, int]] = []
    for r in range(rows - 1):
        for c in range(cols - 1):
            if (r, c) not in visited and grid[r][c] == 2 and grid[r][c + 1] == 2 \
                    and grid[r + 1][c] == 2 and grid[r + 1][c + 1] == 2:
                blocks.append((r, c))
                visited.update([(r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)])
    return blocks


def solve(grid: List[List[int]]) -> List[List[int]]:
    out = [row[:] for row in grid]
    blocks = _find_blocks(grid)
    blocks_sorted = sorted(blocks, key=lambda b: b[1])
    n = len(blocks_sorted)
    for j, (r, c) in enumerate(blocks_sorted):
        idx_from_right = n - 1 - j
        color = 8 if idx_from_right % 2 == 0 else 2
        out[r][c] = out[r][c + 1] = color
        out[r + 1][c] = out[r + 1][c + 1] = color
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
