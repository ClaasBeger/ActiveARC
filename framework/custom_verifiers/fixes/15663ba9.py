"""15663ba9: mark every corner of every loop, outside or inside.

Loops of one colour lie on an empty field. Each cell where a loop turns is
marked: yellow where the bend wraps around ground the loop shuts in, red where
it wraps around open ground. Straight stretches are left alone.

The vendored verifier decides "inside" by flooding the whole picture from the
border, so a pocket that two different loops happen to seal between them counts
as inside for both of them and its corners come out yellow. A loop's inside is a
property of that loop alone, so each one is flooded on its own here, with the
other loops treated as open ground.
"""
from typing import List, Set, Tuple

Grid = List[List[int]]

CONVEX = 4
CONCAVE = 2


def _components(grid: Grid) -> List[Set[Tuple[int, int]]]:
    h, w = len(grid), len(grid[0])
    seen = [[False] * w for _ in range(h)]
    out: List[Set[Tuple[int, int]]] = []
    for r in range(h):
        for c in range(w):
            if seen[r][c] or grid[r][c] == 0:
                continue
            colour = grid[r][c]
            stack = [(r, c)]
            seen[r][c] = True
            cells = set()
            while stack:
                y, x = stack.pop()
                cells.add((y, x))
                for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                    if (0 <= ny < h and 0 <= nx < w and not seen[ny][nx]
                            and grid[ny][nx] == colour):
                        seen[ny][nx] = True
                        stack.append((ny, nx))
            out.append(cells)
    return out


def _inside(grid: Grid, loop: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
    """The cells this loop shuts in, with every other loop treated as open."""
    h, w = len(grid), len(grid[0])
    reached = [[False] * w for _ in range(h)]
    stack = []
    for r in range(h):
        for c in (0, w - 1):
            if (r, c) not in loop and not reached[r][c]:
                reached[r][c] = True
                stack.append((r, c))
    for c in range(w):
        for r in (0, h - 1):
            if (r, c) not in loop and not reached[r][c]:
                reached[r][c] = True
                stack.append((r, c))
    while stack:
        y, x = stack.pop()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if (0 <= ny < h and 0 <= nx < w and not reached[ny][nx]
                    and (ny, nx) not in loop):
                reached[ny][nx] = True
                stack.append((ny, nx))
    return {(r, c) for r in range(h) for c in range(w)
            if not reached[r][c] and (r, c) not in loop}


def solve(grid: Grid) -> Grid:
    h = len(grid)
    w = len(grid[0]) if h else 0
    if h == 0 or w == 0 or any(len(row) != w for row in grid):
        return [list(row) for row in grid]
    out = [list(row) for row in grid]
    for loop in _components(grid):
        inside = _inside(grid, loop)
        for r, c in loop:
            up = (r - 1, c) in loop
            down = (r + 1, c) in loop
            left = (r, c - 1) in loop
            right = (r, c + 1) in loop
            # A corner has exactly one neighbour each way; a straight run or a
            # junction has none or two.
            if (up == down) or (left == right):
                continue
            dr = -1 if up else 1
            dc = -1 if left else 1
            # The cell the turn wraps around. Wrapping around a cell the loop
            # shuts in is the outer side of the bend; wrapping around open
            # ground is the inner side.
            out[r][c] = CONVEX if (r + dr, c + dc) in inside else CONCAVE
    return out
