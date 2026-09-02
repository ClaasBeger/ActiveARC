"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ca8de6ea
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[421](id=421)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0421__ca8de6ea
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    main = [grid[i][i] for i in range(5)]
    anti = [grid[i][4 - i] for i in range(5)]
    out = [[0] * 3 for _ in range(3)]
    out[0][0] = main[0]
    out[0][1] = main[1]
    out[0][2] = anti[0]
    out[1][0] = anti[1]
    out[1][1] = main[2]
    out[1][2] = anti[3]
    out[2][0] = anti[4]
    out[2][1] = main[3]
    out[2][2] = main[4]
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
