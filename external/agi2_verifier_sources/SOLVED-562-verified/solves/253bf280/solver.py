def solve(grid):
    h, w = len(grid), len(grid[0])
    out = [row[:] for row in grid]
    for r in range(h):
        cols = [c for c in range(w) if grid[r][c] == 8]
        if len(cols) >= 2:
            a, b = cols[0], cols[-1]
            if all(grid[r][c] == 0 for c in range(a + 1, b)):
                for c in range(a + 1, b):
                    out[r][c] = 3
    for c in range(w):
        rows = [r for r in range(h) if grid[r][c] == 8]
        if len(rows) >= 2:
            a, b = rows[0], rows[-1]
            if all(grid[r][c] == 0 for r in range(a + 1, b)):
                for r in range(a + 1, b):
                    out[r][c] = 3
    return out
