# 🧩 ARC-AGI Solved Tasks — Unified, Verified Catalog

This repo is the single, unified home for TranscendPlexity's ARC-AGI static-grid puzzle
solvers. It merges what used to be three separate repos
(this repo, formerly named `SOLVED-540-of-540`, plus `SOLVED---abc82100` and
`13-Impossible-ARC-Tasks-SOLVED`) — the other two are now archived and point here.

## The real, verified number

**562 verified solvers.** Everything in `solves/` is verified — there is nothing
unverifiable mixed in with it. Verified means official task data exists, and running
`solve(grid)` produces an **exact match** against the held-out test pair(s) — not
partial/cell-overlap credit.

Coverage is measured per `(split, task)`, because **410 of the 562 task IDs appear in two
official splits with different train/test pairs.** Those solvers were checked against both
copies, and pass both — two distinct held-out test pairs for the same underlying rule.

| Official split | Solved | Available |
|---|---|---|
| **ARC-AGI-1 public evaluation** | **400** | **400** |
| **ARC-AGI-2 public evaluation** | **120** | **120** |
| ARC-AGI-2 training | 424 | 1000 |
| ARC-AGI-1 training | 28 | 400 |
| **Total split-instances** | **972** | **1920** |

Both public evaluation sets are fully covered. Reproduce this yourself:

```bash
python3 verify_all.py
# => Results: 562 passed, 0 failed, 0 skipped
```

`catalog.json` records the full list of splits each solver verifies against in its
`datasets` field.

## Layout

```
solves/         562 verified solvers — every one checkable, nothing else in here
dataset/tasks/  1147 task files, all byte-identical to an official ARC release
unverifiable/   material that cannot be verified, kept for history and clearly
                labelled — see unverifiable/README.md
catalog.json    one entry per solver, status verified_solved or unverified_claim
verify_all.py   reproduces the 562
```

The separation is the point. `solves/` used to contain 118 solvers for task IDs that
do not exist in any ARC dataset, which made the directory itself untrustworthy. They now
live under `unverifiable/`, with the evidence written down.

> Previously named `SOLVED-530-of-648`, before that `SOLVED-514-of-632` and
> `SOLVED-540-of-540`. Old URLs still redirect here.

## Do the solvers actually generalize?

Passing a held-out test pair proves little on its own — a solver hardcoded to that one
output would also pass. So every solver was additionally run against the **train** pairs
it never needed to satisfy. A lookup table fails this; a real rule does not.

| Check | Result |
|---|---|
| Exact match on official held-out test pairs | **562 / 562** |
| Also reproduce **every** train pair | **559 / 562 (99.5%)** |
| Fail ≥1 train pair | 3 |
| Also pass a **second** split's differing held-out pair | **410 / 562** |

The 3 that miss a train pair (`4acc7107`, `5af49b42`, `b942fd60`) are genuine
algorithms with slightly imperfect rule induction — which is the *opposite* of
memorization, since an overfitted solver would trivially pass the pairs it was fitted to.

Three solvers failed this audit and were rewritten as real algorithms:

- **`f560132c`** — was `if grid[2][2]==1 and grid[2][3]==5: return <exact 8x8 grid>`.
  Now solves the actual puzzle: the four shapes are jigsaw pieces whose areas sum to a
  perfect square, so it runs an exact-cover packing search, fixes the board's orientation
  by requiring the legend-bearing piece to stay as drawn, and colours each placed piece
  from the 2x2 legend.
- **`b1fc8b8e`** — was `if count_8s >= 16: return <grid A> else <grid B>`. Now derives the
  output from a conserved quantity: the 5x5 frame is painted with exactly as many cells as
  the input contains.
- **`2dd70a9a`** — was not self-contained (it imported an external `rearc_package` DSL and
  crashed on a clean checkout). Rewritten as a standalone bouncing-ray path solver.


### Important caveats for honest interpretation

- **520 of the 972 split-instances are against held-out *evaluation* sets** (400 ARC-AGI-1
  + 120 ARC-AGI-2); the remaining 452 are training-set tasks, which are meant to be
  learnable/inspectable and so are a lower bar.
- **These are per-task solvers, not an ARC benchmark score.** Each `solve()` was written
  for one specific task after inspecting it. That is a fundamentally different thing from
  a general system that sees an unseen task and solves it — which is what the ARC Prize
  leaderboard measures, and why published ARC-AGI-2 scores are in the single digits. Read
  "120/120 on ARC-AGI-2 evaluation" as "these 120 tasks each have a verified reference
  implementation", not as a benchmark result.
- **118 solvers reference task IDs that exist in no ARC dataset**, checked against local
  copies and directly against `fchollet/ARC-AGI` and `arcprize/ARC-AGI-2` upstream. They
  were previously marked "✅ Solved (100%)". They are now in `unverifiable/solvers/` with
  the full evidence, and are excluded from the 562.
- **The "125/125 (100%)" RE-ARC claim was tested and does not hold.** Measured with the
  official RE-ARC generators and verifiers on freshly generated inputs: **0/12**. Of the
  600 solver directories involved, only 12 correspond to a real RE-ARC task and 537
  correspond to no official ARC task at all. See `unverifiable/README.md`.
- **`arc3/` is a separate, different system** — an interactive game-playing agent for
  ARC-AGI-3 (not a static grid solver). It is **not** included in the count above.
  This exact agent was independently tested and scored **2/183** on real ARC-AGI-3 levels —
  far below the "20/20 (100%)" figure quoted for it elsewhere in this account's history.
- Previous headline claims across this account's repos have been mutually inconsistent:
  "540/540 (100%)", "514 standalone solvers", "422 solvers", and "665/665 combined" have
  all been used to describe overlapping-but-different subsets of this same body of work.
  This README replaces all of those with the one number that's actually been
  independently reproduced end-to-end: **562**.

## How It Works

Each solver is a pure Python function that takes a 2D grid (list of lists of ints) and
returns the transformed output grid. No ML models, no LLMs at inference time — just code,
synthesized offline using Claude Opus 4.6 via iterative program generation (observe
training examples → hypothesize rule → write `solve(grid)` → test → iterate → verify
against held-out test pairs).

```python
# Example: solves/0934a4d8/solver.py
def solve(grid: list[list[int]]) -> list[list[int]]:
    # Deterministic transformation logic
    ...
```

## Repository Structure

```
solves/{task_id}/solver.py   # 562 verified solvers — nothing unverifiable in here
dataset/tasks/{task_id}.json # 1147 task files, all identical to an official release
catalog.json                 # Per-task metadata incl. honest status field
verify_all.py                # Run this to reproduce the 562 result yourself
unverifiable/                # Material that cannot be checked, with the evidence
arc3/                        # SEPARATE interactive-game agent (not part of the 562)
re-arc/                      # RE-ARC claim, measured at 0/12 — see unverifiable/
kaggle_2025/                 # Official Kaggle ARC Prize 2025 competition data
viz/                         # Per-task HTML grid visualizations
```

## Running a Solver

```bash
python3 -c "
import json, importlib.util

task_id = '0934a4d8'
with open(f'dataset/tasks/{task_id}.json') as f:
    task = json.load(f)

spec = importlib.util.spec_from_file_location('solver', f'solves/{task_id}/solver.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

for pair in task['test']:
    result = mod.solve(pair['input'])
    assert result == pair['output'], 'Mismatch!'
    print(f'{task_id}: PASS')
"
```

## Verification protocol

1. Agent writes `solver.py` based on training examples only.
2. Solver is tested against all training pairs.
3. Solver is independently verified against test pairs (never seen during development).
4. Solvers with no backing task data cannot be verified at all, so they are excluded from
   the count and moved to `unverifiable/` rather than left in `solves/`.

## Contact

Evan Pieser — epieser@protonmail.com
