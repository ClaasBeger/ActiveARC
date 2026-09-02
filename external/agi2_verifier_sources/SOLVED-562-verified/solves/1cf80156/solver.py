def solve(grid):
    cells = [(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v != 0]
    r0 = min(r for r, _ in cells)
    r1 = max(r for r, _ in cells)
    c0 = min(c for _, c in cells)
    c1 = max(c for _, c in cells)
    return [row[c0:c1 + 1] for row in grid[r0:r1 + 1]]
