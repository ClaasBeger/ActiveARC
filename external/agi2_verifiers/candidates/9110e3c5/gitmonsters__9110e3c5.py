"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9110e3c5
source: GitMonsters/SOLVED-562-verified
original_path: solves/9110e3c5/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__9110e3c5
"""
from __future__ import annotations



from collections import Counter


PATTERNS = {
    1: [[0, 0, 8], [8, 8, 0], [0, 8, 0]],
    2: [[0, 0, 0], [8, 8, 8], [0, 0, 0]],
    3: [[0, 8, 8], [0, 8, 0], [0, 8, 0]],
}


def solve(grid: list[list[int]]) -> list[list[int]]:
    counts = Counter(v for row in grid for v in row if v != 0)
    dominant = counts.most_common(1)[0][0]
    return PATTERNS[dominant]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
