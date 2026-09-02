"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: cad67732
source: GitMonsters/SOLVED-562-verified
original_path: solves/cad67732/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__cad67732
"""
from __future__ import annotations



"""
Solver for ARC-AGI task cad67732.

Rule: The input NxN grid contains a periodic diagonal band (main or anti-diagonal).
The output is 2Nx2N with the same periodic band extended to fill the larger grid.
"""


def solve(grid: list[list[int]]) -> list[list[int]]:
    N = len(grid)
    M = 2 * N

    non_zero = [(r, c) for r in range(N) for c in range(N) if grid[r][c] != 0]
    output = [[0] * M for _ in range(M)]

    if not non_zero:
        return output

    # Detect whether band follows main diagonal (r-c ≈ 0) or anti-diagonal (r+c ≈ N-1)
    main_spread = sum(abs(r - c) for r, c in non_zero) / len(non_zero)
    anti_spread = sum(abs(r + c - (N - 1)) for r, c in non_zero) / len(non_zero)

    def find_period(vals: list[int]) -> int:
        n = len(vals)
        for p in range(1, n + 1):
            if all(vals[i] == vals[i % p] for i in range(n)):
                return p
        return n

    if main_spread <= anti_spread:
        # Main diagonal band: parameterize by d = r - c
        for d in range(-(N - 1), N):
            vals = []
            for k in range(N - abs(d)):
                r = max(d, 0) + k
                c = max(-d, 0) + k
                vals.append(grid[r][c])

            if all(v == 0 for v in vals):
                continue

            period = find_period(vals)

            for k in range(M - abs(d)):
                r = max(d, 0) + k
                c = max(-d, 0) + k
                output[r][c] = vals[k % period]
    else:
        # Anti-diagonal band: parameterize by d = r + c, shift by N in output
        for d in range(2 * N - 1):
            r_start = max(0, d - (N - 1))
            r_end = min(N - 1, d)

            vals = []
            for r in range(r_start, r_end + 1):
                vals.append(grid[r][d - r])

            if all(v == 0 for v in vals):
                continue

            period = find_period(vals)

            d_out = d + N
            r_start_out = max(0, d_out - (M - 1))
            r_end_out = min(M - 1, d_out)

            for r in range(r_start_out, r_end_out + 1):
                c = d_out - r
                idx = (r - r_start_out) % period
                output[r][c] = vals[idx]

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
