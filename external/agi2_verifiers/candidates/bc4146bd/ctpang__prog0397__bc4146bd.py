"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: bc4146bd
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[397](id=397)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0397__bc4146bd
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid_lst: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid_lst)
    flip = np.fliplr(grid)
    result = np.hstack([grid, flip, grid, flip, grid])
    return result.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
