def solve(grid):
    out = [row[:] for row in grid]
    for r, row in enumerate(grid):
        cols = [c for c, v in enumerate(row) if v != 0]
        if len(cols) >= 2 and row[cols[0]] == row[cols[-1]]:
            for c in range(cols[0], cols[-1] + 1):
                out[r][c] = row[cols[0]]
    return out
