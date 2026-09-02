"""Solver for ARC-AGI-2 task f560132c.

Rule (induced from the grid, not memorised):

* The grid holds exactly four separate shapes. Their cell counts always sum to
  a perfect square N*N -- they are jigsaw pieces of an N x N board.
* One shape (the "key") carries a 2x2 legend of four foreign colours embedded
  inside it. The legend's layout is a map of the finished board: its top-left
  colour belongs to the piece that ends up in the board's top-left, and so on.
* The packing is unique up to the square's 8 symmetries, so the board's
  orientation is fixed by requiring the key piece to sit exactly as it is drawn
  in the input -- it is the one piece that is never rotated or reflected.
* Solve the packing, then paint each placed piece with the legend colour whose
  quadrant matches that piece's centroid.
"""

from collections import deque
from itertools import permutations
from typing import Dict, List, Optional, Set, Tuple

Grid = List[List[int]]
Cell = Tuple[int, int]


def _components(grid: Grid) -> List[List[Cell]]:
    """Connected groups of non-zero cells (colour-blind, so an embedded
    legend stays part of the shape that contains it)."""
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    out: List[List[Cell]] = []
    for r in range(rows):
        for c in range(cols):
            if not grid[r][c] or seen[r][c]:
                continue
            queue = deque([(r, c)])
            seen[r][c] = True
            cells: List[Cell] = []
            while queue:
                y, x = queue.popleft()
                cells.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if (0 <= ny < rows and 0 <= nx < cols
                            and grid[ny][nx] and not seen[ny][nx]):
                        seen[ny][nx] = True
                        queue.append((ny, nx))
            out.append(cells)
    return out


def _find_legend(grid: Grid, cells: List[Cell]) -> Optional[List[List[int]]]:
    """A 2x2 block of four cells whose colours all differ from the shape's own
    dominant colour. Returns it as a 2x2 colour map, or None."""
    counts: Dict[int, int] = {}
    for y, x in cells:
        counts[grid[y][x]] = counts.get(grid[y][x], 0) + 1
    body = max(counts, key=lambda k: counts[k])
    foreign = {(y, x) for y, x in cells if grid[y][x] != body}
    if len(foreign) != 4:
        return None
    ys = sorted({y for y, _ in foreign})
    xs = sorted({x for _, x in foreign})
    if len(ys) != 2 or len(xs) != 2:
        return None
    if ys[1] - ys[0] != 1 or xs[1] - xs[0] != 1:
        return None
    return [[grid[ys[0]][xs[0]], grid[ys[0]][xs[1]]],
            [grid[ys[1]][xs[0]], grid[ys[1]][xs[1]]]]


def _normalise(cells) -> Tuple[Cell, ...]:
    my = min(y for y, _ in cells)
    mx = min(x for _, x in cells)
    return tuple(sorted((y - my, x - mx) for y, x in cells))


def _orientations(cells: List[Cell]) -> List[Tuple[Cell, ...]]:
    """All 8 rotations/reflections, de-duplicated."""
    seen: Set[Tuple[Cell, ...]] = set()
    cur = list(cells)
    for _ in range(4):
        cur = [(x, -y) for y, x in cur]
        for variant in (cur, [(y, -x) for y, x in cur]):
            seen.add(_normalise(variant))
    return sorted(seen)


def _pack(pieces: List[List[Tuple[Cell, ...]]], n: int) -> Optional[List[int]]:
    """Exact-cover backtracking: board[i] = index of the piece covering cell i."""
    board = [-1] * (n * n)

    def recurse(used: int) -> bool:
        if used == (1 << len(pieces)) - 1:
            return True
        try:
            slot = board.index(-1)
        except ValueError:
            return False
        sr, sc = divmod(slot, n)
        for pi, variants in enumerate(pieces):
            if used & (1 << pi):
                continue
            for shape in variants:
                # anchor the shape's first cell on the first empty slot
                ay, ax = shape[0]
                placed = []
                ok = True
                for dy, dx in shape:
                    y, x = sr + dy - ay, sc + dx - ax
                    if not (0 <= y < n and 0 <= x < n) or board[y * n + x] != -1:
                        ok = False
                        break
                    placed.append(y * n + x)
                if not ok:
                    continue
                for idx in placed:
                    board[idx] = pi
                if recurse(used | (1 << pi)):
                    return True
                for idx in placed:
                    board[idx] = -1
        return False

    return board if recurse(0) else None


def solve(grid: Grid) -> Grid:
    shapes = _components(grid)

    key = None
    legend = None
    for index, cells in enumerate(shapes):
        found = _find_legend(grid, cells)
        if found is not None:
            key, legend = index, found
            break
    if legend is None:
        raise ValueError("no 2x2 legend found")

    total = sum(len(c) for c in shapes)
    n = int(round(total ** 0.5))
    if n * n != total:
        raise ValueError("piece areas do not form a square")

    # Pinning the key piece to its input orientation selects one board out of
    # the eight symmetric packings.
    variants = [_orientations(c) for c in shapes]
    variants[key] = [_normalise(shapes[key])]

    packing = _pack(variants, n)
    if packing is None:
        raise ValueError("no packing found")

    # Match pieces to legend quadrants as a whole: an irregular piece can drift
    # out of "its" quadrant, so choose the assignment that minimises the total
    # squared distance between piece centroids and quadrant centres.
    centroids = []
    for index in range(len(shapes)):
        cells = [divmod(i, n) for i, p in enumerate(packing) if p == index]
        centroids.append((sum(y for y, _ in cells) / len(cells),
                          sum(x for _, x in cells) / len(cells)))

    quadrants = [(qr, qc) for qr in (0, 1) for qc in (0, 1)]
    targets = [((2 * qr + 1) * n / 4, (2 * qc + 1) * n / 4) for qr, qc in quadrants]

    best = min(
        permutations(range(len(shapes))),
        key=lambda order: sum(
            (centroids[p][0] - targets[q][0]) ** 2
            + (centroids[p][1] - targets[q][1]) ** 2
            for q, p in enumerate(order)
        ),
    )
    colour_of = {p: legend[quadrants[q][0]][quadrants[q][1]]
                 for q, p in enumerate(best)}

    return [[colour_of[packing[r * n + c]] for c in range(n)] for r in range(n)]


if __name__ == "__main__":
    import json
    import sys

    with open(sys.argv[1]) as fh:
        task = json.load(fh)
    for split in ("train", "test"):
        for i, pair in enumerate(task[split]):
            got = solve(pair["input"])
            print(f"{split}[{i}]: {'PASS' if got == pair['output'] else 'FAIL'}")
