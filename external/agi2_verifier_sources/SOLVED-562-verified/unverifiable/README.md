# Unverifiable material

Nothing in this directory is part of the verified count in the top-level README.
It is kept for history, clearly separated from `solves/`, so that `solves/` can
be a directory where every single entry is checkable.

## `solvers/` — 118 solvers for task IDs that do not exist

These were previously in `solves/` and previously marked "✅ Solved (100%)" in
`catalog.json`, with no data behind that claim.

What was checked:

- Their task IDs appear in **no** official dataset — not ARC-AGI-1 training or
  evaluation, not ARC-AGI-2 training or evaluation. Confirmed both against local
  copies and directly against `fchollet/ARC-AGI` and `arcprize/ARC-AGI-2`
  upstream, which return 404 for every one sampled.
- An index of all 15,341 ARC-style task JSON files on the authoring machine
  found matching data for exactly **1 of 118**, and that one hit was a copy of
  this same repo.
- **116 of the 118 define `transform()` and never define `solve()`**, so they do
  not implement this catalog's interface and would fail `verify_all.py`
  regardless of whether data existed.
- 13 of them read task data from `/tmp/rearc45/`, a scratch directory that no
  longer exists — so they were written against procedurally generated tasks that
  were never persisted.
- One (`0ae0773b`) states its own method in a comment: *"Memorize degenerate
  training pairs."*

The most likely explanation is that these were written against RE-ARC-generated
tasks living in `/tmp`, and the generated IDs were then recorded as if they were
official ARC task IDs.

## `re-arc-solvers/` — 600 solvers behind a "125/125 (100%)" claim

The old `re-arc/README.md` claimed **125/125 (100%)** on the RE-ARC benchmark.
That claim was tested directly and does not hold.

RE-ARC tasks are procedurally generated, so there is no fixed test pair to check
against. The correct test is to generate fresh examples with the official
generator and see whether the solver agrees with the official verifier on inputs
it has never seen. Using `generators.py` / `verifiers.py` from the RE-ARC
package (400 generator/verifier pairs), 10 fresh examples per task:

| Measure | Result |
|---|---|
| Solver directories present | 600 (not 125) |
| Correspond to a real RE-ARC task (ARC-AGI-1 training) | **12** |
| Correspond to **no** official ARC task at all | **537** |
| Of the 12 real ones: 100% agreement with the official verifier | **0** |
| Partial agreement | 3 |
| Zero agreement | 9 |

So the measured result is **0 / 12**, against a claim of 125/125.

32 solvers that were sitting in this directory *did* verify against official
ARC-AGI-2 training tasks, and those have been promoted into `solves/`. They are
counted in the top-level total. The rest remain here.
