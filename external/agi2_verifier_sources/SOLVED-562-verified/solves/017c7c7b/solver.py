def solve(grid):
    rows = [[2 if x == 1 else x for x in row] for row in grid]
    period = 1
    while period <= len(rows):
        if all(rows[i] == rows[i % period] for i in range(len(rows))):
            break
        period += 1
    return [rows[i % period][:] for i in range(9)]
