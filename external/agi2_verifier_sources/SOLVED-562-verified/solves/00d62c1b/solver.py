from collections import deque

def solve(grid):
    h, w = len(grid), len(grid[0])
    seen = [[False] * w for _ in range(h)]
    q = deque()
    for r in range(h):
        for c in (0, w - 1):
            if grid[r][c] == 0 and not seen[r][c]:
                seen[r][c] = True
                q.append((r, c))
    for c in range(w):
        for r in (0, h - 1):
            if grid[r][c] == 0 and not seen[r][c]:
                seen[r][c] = True
                q.append((r, c))
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == 0 and not seen[nr][nc]:
                seen[nr][nc] = True
                q.append((nr, nc))
    out = [row[:] for row in grid]
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 0 and not seen[r][c]:
                out[r][c] = 4
    return out
