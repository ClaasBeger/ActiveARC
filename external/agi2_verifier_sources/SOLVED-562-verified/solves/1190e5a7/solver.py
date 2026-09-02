def solve(grid):
    h, w = len(grid), len(grid[0])
    colors = {v for row in grid for v in row if v}
    sep = None
    for color in colors:
        if any(all(v == color for v in row) for row in grid) or any(all(grid[r][c] == color for r in range(h)) for c in range(w)):
            sep = color
            break
    fill = max((v for v in colors if v != sep), key=lambda x: sum(v == x for row in grid for v in row))
    full_rows = sum(all(v == sep for v in row) for row in grid)
    full_cols = sum(all(grid[r][c] == sep for r in range(h)) for c in range(w))
    return [[fill] * (full_cols + 1) for _ in range(full_rows + 1)]
