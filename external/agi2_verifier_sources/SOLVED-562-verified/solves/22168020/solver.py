def solve(grid):
    out = [row[:] for row in grid]
    for color in {v for row in grid for v in row if v}:
        for r, row in enumerate(grid):
            cols = [c for c, v in enumerate(row) if v == color]
            if len(cols) >= 2:
                for c in range(min(cols), max(cols) + 1):
                    out[r][c] = color
    return out
