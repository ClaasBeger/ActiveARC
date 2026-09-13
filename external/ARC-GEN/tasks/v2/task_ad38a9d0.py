# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Generator."""

import common

_MAX_PLACEMENTS = 200

# Cell offsets of each shape, keyed by its color.
_SHAPES = {
    2: ((0, 0), (1, 0), (2, 0)),
    3: ((0, 1), (1, 0), (1, 1), (1, 2), (2, 1)),
    4: ((0, 0), (0, 1), (1, 1)),
    5: ((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)),
    8: ((0, 0), (0, 1), (1, 1), (1, 2)),
    9: ((0, 0), (1, 0)),
}
_TALLS = {color: max(dr for dr, _ in s) + 1 for color, s in _SHAPES.items()}
_WIDES = {color: max(dc for _, dc in s) + 1 for color, s in _SHAPES.items()}


def generate(rows=None, cols=None, colors=None):
  """Returns input and output grids according to the given parameters.

  Args:
    rows: The rows of the shapes.
    cols: The columns of the shapes.
    colors: The colors of the shapes.
  """

  def draw():
    index = -1
    bad = False
    grid, output = common.grids(9, 9, 7)
    hidden = common.grid(9, 9, -1)
    def put(r, c, color):
      nonlocal index, bad, grid, output, hidden
      if grid[r][c] != 7: bad = True
      grid[r][c] = 6
      output[r][c] = color
      hidden[r][c] = index
    for row, col, color in zip(rows, cols, colors):
      index += 1
      for dr, dc in _SHAPES[color]:
        put(row + dr, col + dc, color)
    # Check that no two colors share an adjacent edge.
    for r in range(9):
      for c in range(8):
        if hidden[r][c] == -1 or hidden[r][c + 1] == -1: continue
        if hidden[r][c] != hidden[r][c + 1]: bad = True
    for r in range(8):
      for c in range(9):
        if hidden[r][c] == -1 or hidden[r + 1][c] == -1: continue
        if hidden[r][c] != hidden[r + 1][c]: bad = True
    if bad: return None, None
    return grid, output

  if rows is None:
    while True:
      # The number of extra shapes is redrawn on every restart, so a count the
      # grid cannot hold cannot wedge the loop.
      extra = common.randint(0, 2)
      colors = [2, 3, 4, 5, 8, 9]
      colors += common.sample(colors, extra)
      colors = common.shuffle(colors)
      # Place the shapes one at a time, retrying only the shape that fails to
      # fit.  Drawing every position at once and rejecting the whole layout
      # essentially never lands eight mutually non-adjacent shapes on a 9x9
      # grid, which is the case the first official example uses.
      rows, cols, taken = [], [], {}
      for index, color in enumerate(colors):
        for _ in range(_MAX_PLACEMENTS):
          row = common.randint(0, 9 - _TALLS[color])
          col = common.randint(0, 9 - _WIDES[color])
          cells = [(row + dr, col + dc) for dr, dc in _SHAPES[color]]
          # A shape may neither overlap nor share an edge with another shape.
          if any(taken.get((r + dr, c + dc), index) != index
                 for r, c in cells
                 for dr, dc in ((0, 0), (0, 1), (0, -1), (1, 0), (-1, 0))): continue
          for cell in cells: taken[cell] = index
          rows.append(row)
          cols.append(col)
          break
        else:
          break
      if len(rows) < len(colors): continue
      grid, _ = draw()
      if grid: break

  grid, output = draw()
  return {"input": grid, "output": output}


def validate():
  """Validates the generator."""
  train = [
      generate(rows=[0, 0, 2, 2, 3, 4, 6, 7], cols=[0, 4, 2, 8, 6, 1, 7, 4],
               colors=[4, 8, 3, 2, 9, 2, 4, 5]),
      generate(rows=[1, 1, 2, 5, 6, 7], cols=[0, 4, 6, 4, 8, 1],
               colors=[3, 9, 4, 8, 2, 5]),
  ]
  test = [
      generate(rows=[0, 0, 2, 3, 6, 6, 7], cols=[0, 4, 8, 3, 0, 7, 5],
               colors=[3, 8, 2, 5, 4, 4, 9]),
  ]
  return {"train": train, "test": test}
