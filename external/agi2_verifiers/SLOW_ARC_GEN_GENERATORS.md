# Slow ARC-GEN generators (temporary note)

Delete this file after migrating and resolving validation for the listed tasks.

## Affected tasks

| Task ID | Generator file | Blocked verifier candidate |
|---------|----------------|--------------------------|
| `6ffe8f07` | `external/ARC-GEN/tasks/v2/task_6ffe8f07.py` | `ctpang__prog0239__6ffe8f07` |
| `e681b708` | `external/ARC-GEN/tasks/v2/task_e681b708.py` | `gitmonsters__e681b708` |

Related (not a generator issue): `2c0b0aff` / `gitmonsters__2c0b0aff` fails validation on dynamics (wrong output); treat as **invalid**, not pending.

## Symptom

Dynamic pair collection for validation (`250` seeds × `verify()`) hangs or exceeds worker budgets. Pass 5 left the two candidates above as `pending_timeout` with `official 0/0 dyn=0/0` because generation never finished inside the worker.

Validation reads/writes caches under:

`external/agi2_verifiers/logs/dynamic_cache/{task_id}_250.json`

**Those two cache files are currently missing** (built once, then deleted by an early pass-5 retry that cleared caches). Regenerating them takes roughly **11 min (`6ffe8f07`) + 27 min (`e681b708`) ≈ 40 min** total on this machine. Do **not** clear existing caches before retrying pending verifiers.

## Root cause

Both generators use unbounded `while True` rejection sampling:

- **`6ffe8f07`**: pack `4–12` non-overlapping rectangles on an `18×19` grid; ~47% of seeds never find a valid layout (some draw too many/large boxes).
- **`e681b708`**: random grid + line layout, then an expensive `draw()` with many geometric/color constraints; ~54% of seeds fail; successful seeds often need **2–8 s** (many were rejected by the old **2 s** generation alarm).

The verifiers themselves are fast on official pairs; the bottleneck is **ARC-GEN sampling**, not `verify()`.

## Fixes already applied

1. **Bounded rejection** (`_MAX_ATTEMPTS = 100_000`, then `RuntimeError`) in both task files — same output for seeds that succeed; hopeless seeds fail fast instead of spinning forever.
2. **`GENERATION_TIMEOUT_S = 10.0`** in `scripts/import_agi2_verifiers/validate.py` (was `2.0`) — allows slow-but-valid `e681b708` seeds to complete.
3. **`retry_pending_timeouts.py`** no longer deletes dynamic caches before retry.

## To finish validation (after cache regen)

```bash
# One-time cache build (slow; run once, keep the JSON files)
python3 - <<'PY'
import sys; sys.path.insert(0, ".")
from scripts.import_agi2_verifiers.validate import _generate_dynamic_pairs, N_DYNAMIC
for tid in ("6ffe8f07", "e681b708"):
    pairs, fails = _generate_dynamic_pairs(tid, N_DYNAMIC)
    print(tid, len(pairs), fails)
PY

# Then retry pending (fast if caches exist)
python3 scripts/import_agi2_verifiers/retry_pending_timeouts.py
```

With caches present, retry should finish in seconds per candidate (verifier only), not ~40 minutes.
