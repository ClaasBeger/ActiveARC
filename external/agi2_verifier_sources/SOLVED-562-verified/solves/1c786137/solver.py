def solve(grid):
    h, w = len(grid), len(grid[0])
    best = None
    for color in {v for row in grid for v in row if v}:
        cells = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == color]
        r0 = min(r for r, _ in cells)
        r1 = max(r for r, _ in cells)
        c0 = min(c for _, c in cells)
        c1 = max(c for _, c in cells)
        area = (r1 - r0 + 1) * (c1 - c0 + 1)
        if best is None or area < best[0]:
            best = (area, r0, r1, c0, c1)
    _, r0, r1, c0, c1 = best
    return [row[c0 + 1:c1] for row in grid[r0 + 1:r1]]
