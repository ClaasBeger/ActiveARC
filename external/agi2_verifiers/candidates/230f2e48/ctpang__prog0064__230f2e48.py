"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 230f2e48
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[64](id=64)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0064__230f2e48
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    h = len(grid)
    w = len(grid[0])
    output = [row[:] for row in grid]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    def get_chain(sr, sc):
        chain = [(sr, sc)]
        cr, cc = sr, sc
        while True:
            next_pos = None
            count = 0
            for dr, dc in directions:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] != 7 and (nr, nc) not in chain:
                    next_pos = (nr, nc)
                    count += 1
            if count == 0:
                return chain
            if count > 1:
                return []  # Assume no branches
            chain.append(next_pos)
            cr, cc = next_pos
    
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 5:
                chain = get_chain(r, c)
                if len(chain) <= 1:
                    continue
                black_idx = -1
                for i, (rr, cc) in enumerate(chain):
                    if grid[rr][cc] == 0:
                        black_idx = i
                        break
                if black_idx < 0 or black_idx + 1 >= len(chain):
                    continue
                prev_r, prev_c = chain[black_idx - 1]
                black_r, black_c = chain[black_idx]
                dr = black_r - prev_r
                dc = black_c - prev_c
                perp1_dr, perp1_dc = dc, -dr
                perp2_dr, perp2_dc = -dc, dr
                perps = [(perp1_dr, perp1_dc), (perp2_dr, perp2_dc)]
                max_space = -1
                best_perp = None
                for pdr, pdc in perps:
                    if pdr == 0 and pdc == 0:
                        continue
                    if pdr == 0:
                        if pdc > 0:
                            space = w - black_c - 1
                        else:
                            space = black_c
                    else:
                        if pdr > 0:
                            space = h - black_r - 1
                        else:
                            space = black_r
                    if space > max_space:
                        max_space = space
                        best_perp = (pdr, pdc)
                if best_perp is None or max_space < len(chain) - black_idx - 1:
                    continue
                tail_positions = chain[black_idx + 1:]
                cr, cc = black_r + best_perp[0], black_c + best_perp[1]
                for i, (tr, tc) in enumerate(tail_positions):
                    output[cr][cc] = grid[tr][tc]
                    cr += best_perp[0]
                    cc += best_perp[1]
                for tr, tc in tail_positions:
                    output[tr][tc] = 7
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
