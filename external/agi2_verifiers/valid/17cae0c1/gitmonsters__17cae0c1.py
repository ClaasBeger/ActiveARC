"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 17cae0c1
source: GitMonsters/SOLVED-562-verified
original_path: solves/17cae0c1/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__17cae0c1
"""
from __future__ import annotations



def solve(grid):
    # 3x9 grid split into three 3x3 sections. Each section's 5-pattern determines output color.
    # Pattern lookup: specific 3x3 arrangements of 5s map to specific colors.
    pattern_to_color = {
        ((5,5,5),(5,0,5),(5,5,5)): 3,  # ring
        ((0,0,0),(0,5,0),(0,0,0)): 4,  # center dot
        ((0,0,5),(0,5,0),(5,0,0)): 9,  # anti-diagonal
        ((0,0,0),(0,0,0),(5,5,5)): 1,  # bottom row
        ((5,5,5),(0,0,0),(0,0,0)): 6,  # top row
    }
    result = []
    for r in range(3):
        row = []
        for sec in range(3):
            c_start = sec * 3
            pattern = tuple(
                tuple(grid[rr][c_start + cc] for cc in range(3))
                for rr in range(3)
            )
            color = pattern_to_color[pattern]
            row.extend([color] * 3)
        result.append(row)
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
