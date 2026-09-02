# RE-ARC — measured result: 0 / 12

> This file previously claimed **125/125 (100%)** on the RE-ARC benchmark.
> That claim was tested and does not hold. The solvers have been moved to
> [`../unverifiable/re-arc-solvers/`](../unverifiable/) and the full
> methodology and numbers are documented there.

Summary of what was actually measured, using the official RE-ARC
`generators.py` / `verifiers.py` (400 generator/verifier pairs), generating 10
fresh examples per task:

| Measure | Result |
|---|---|
| Solver directories present | 600 (not 125) |
| Correspond to a real RE-ARC task | 12 |
| Correspond to no official ARC task at all | 537 |
| Achieve 100% agreement with the official verifier | **0** |

RE-ARC generates unbounded variations of each task, so a solver written against
one fixed set of examples will not generally survive it — which is the whole
point of the benchmark, and why the original claim needed checking.

32 solvers from this directory did verify against official ARC-AGI-2 training
tasks and have been promoted into `../solves/`.
