def solve(grid):
    cells = [(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v == 8]
    r0 = min(r for r, _ in cells)
    r1 = max(r for r, _ in cells)
    c0 = min(c for _, c in cells)
    c1 = max(c for _, c in cells)
    out = [row[:] for row in grid]
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            if out[r][c] not in (0, 8):
                out[r][c] = 3
    return out
