def solve(grid):
    colors = [None, None, None]
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v:
                colors[(r + c) % 3] = v
    return [[colors[(r + c) % 3] for c in range(len(grid[0]))] for r in range(len(grid))]
