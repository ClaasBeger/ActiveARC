"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 2685904e
source: GitMonsters/SOLVED-562-verified
original_path: solves/2685904e/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__2685904e
"""
from __future__ import annotations



"""
ARC-AGI solver for task 2685904e

Rule:
- Row 0 has N cells of value 8 (left-aligned).
- Row 6 is a separator (all 5s).
- Row 8 is a "palette" of colored values.
- Count occurrences of each value in the palette. For each position where
  the palette value appears exactly N times, show that value; otherwise 0.
- Fill this pattern into the N rows directly above the separator (rows 6-N through 5).
"""
from collections import Counter


def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    out = [row[:] for row in grid]

    n_eights = sum(1 for v in grid[0] if v == 8)
    palette = grid[8]
    counts = Counter(palette)

    pattern = [v if counts[v] == n_eights else 0 for v in palette]

    for r in range(6 - n_eights, 6):
        out[r] = pattern[:]

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
