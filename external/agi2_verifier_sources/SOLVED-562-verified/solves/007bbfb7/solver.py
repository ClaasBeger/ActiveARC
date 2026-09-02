def solve(grid):
    n, m = len(grid), len(grid[0])
    out = [[0] * (m * m) for _ in range(n * n)]
    for r in range(n):
        for c in range(m):
            if grid[r][c] != 0:
                for i in range(n):
                    for j in range(m):
                        out[r * n + i][c * m + j] = grid[i][j]
    return out
