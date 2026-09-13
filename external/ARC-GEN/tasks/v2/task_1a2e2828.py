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


def generate(width=None, height=None, values=None, thicks=None, cdirs=None,
             colors=None):
  """Returns input and output grids according to the given parameters.

  Args:
    colors: A list of colors to use.
  """

  if width is None:
    base = common.randint(5, 12)
    width, height = base + common.randint(-2, 2), base + common.randint(-2, 2)
    num_h, num_v = base // 4, base // 4
    if base > 8 and common.randint(0, 1): num_h += 1
    if base > 8 and common.randint(0, 1): num_v += 1
    def place_bands(num, extent):
      # Place the bands one at a time, retrying only the band that doesn't fit.
      thicks, vals = [], []
      for _ in range(num):
        for _ in range(200):
          thick = common.randint(1, min(3, extent - 2))
          val = common.randint(1, extent - thick - 1)
          if common.overlaps_1d(vals + [val], thicks + [thick], 1): continue
          thicks, vals = thicks + [thick], vals + [val]
          break
        else:
          return None, None  # This band doesn't fit; redraw the whole set.
      return thicks, vals

    while True:
      h_thicks, h_vals = place_bands(num_h, height)
      if h_thicks is None: continue
      v_thicks, v_vals = place_bands(num_v, width)
      if v_thicks is None: continue
      # Interleave the bands; retry just the interleaving if it ends badly.
      for _ in range(200):
        h_left, h_vleft = list(h_thicks), list(h_vals)
        v_left, v_vleft = list(v_thicks), list(v_vals)
        values, thicks, cdirs = [], [], []
        while h_left or v_left:
          if common.randint(0, 1):
            if not h_left: continue
            thicks, values = thicks + [h_left.pop()], values + [h_vleft.pop()]
            cdirs.append(0)
          else:
            if not v_left: continue
            thicks, values = thicks + [v_left.pop()], values + [v_vleft.pop()]
            cdirs.append(1)
        if cdirs[-1] != cdirs[-2]: break
      else:
        continue
      break
    colors = common.random_colors(len(values))

  grid, output = common.grid(width, height), common.grid(1, 1, colors[-1])
  for value, thick, cdir, color in zip(values, thicks, cdirs, colors):
    if cdir:
      common.rect(grid, thick, height, 0, value, color)
    else:
      common.rect(grid, width, thick, value, 0, color)
  return {"input": grid, "output": output}


def validate():
  """Validates the generator."""
  train = [
      generate(width=12, height=11, values=[1, 4, 6, 8, 3],
               thicks=[1, 2, 2, 1, 2], cdirs=[0, 1, 0, 1, 0],
               colors=[2, 3, 4, 5, 1]),
      generate(width=11, height=9, values=[2, 3, 5, 8], thicks=[1, 2, 2, 1],
               cdirs=[0, 1, 0, 1], colors=[3, 4, 6, 8]),
      generate(width=11, height=11, values=[1, 1, 7, 6, 4],
               thicks=[3, 2, 2, 2, 1], cdirs=[0, 1, 1, 0, 1],
               colors=[1, 2, 8, 4, 6]),
      generate(width=3, height=3, values=[1, 1], thicks=[1, 1], cdirs=[1, 0],
               colors=[1, 3]),
      generate(width=12, height=8, values=[2, 1, 7, 5], thicks=[2, 2, 1, 1],
               cdirs=[0, 1, 1, 0], colors=[3, 2, 8, 6]),
  ]
  test = [
      generate(width=13, height=11, values=[2, 3, 6, 9], thicks=[2, 2, 1, 1],
               cdirs=[0, 1, 0, 1], colors=[1, 3, 6, 7]),
  ]
  return {"train": train, "test": test}
