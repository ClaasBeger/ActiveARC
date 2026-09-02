"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e57337a4
source: GitMonsters/SOLVED-562-verified
original_path: solves/e57337a4/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__e57337a4
"""
from __future__ import annotations



def solve(grid):
    rows = len(grid)
    cols = len(grid[0])
    block = 5
    out_rows = rows // block
    out_cols = cols // block

    # Determine background color (most common)
    counts = {}
    for r in range(rows):
        for c in range(cols):
            v = grid[r][c]
            counts[v] = counts.get(v, 0) + 1
    bg = max(counts, key=counts.get)

    out = []
    for br in range(out_rows):
        row = []
        for bc in range(out_cols):
            has_non_bg = False
            for r in range(br * block, (br + 1) * block):
                for c in range(bc * block, (bc + 1) * block):
                    if grid[r][c] != bg:
                        has_non_bg = True
                        break
                if has_non_bg:
                    break
            row.append(0 if has_non_bg else bg)
        out.append(row)
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
