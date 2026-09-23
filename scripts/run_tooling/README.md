# Run tooling

Helpers used to run and repair the 2026-09 replication and teacher experiments.

- `with_key.sh VARNAME cmd...` — sets `OPENROUTER_API_KEY` from jagEval's stored env var
  `VARNAME` and execs `cmd`. Needed because conda 26.7.1 stopped exporting jagEval's
  `env_vars`, and the shell may hold stale copies. Run it inside `conda run -n jagEval`.
- `mkshards.py`, `mkshards_arc.py` — split a benchmark's task list (the runner's own
  `_task_ids`) into disjoint, interleaved shards; lists land in `shards/<tag>_shard<k>.args`.
  The committed lists are the ones used for the DeepSeek and Opus draws.
- `shard_run.sh` (DeepSeek) / `shard_run_opus.sh` (Opus 5) —
  `OUTDIR DATASET LIMIT TAG SHARD_IDX KEYVAR`: runs one shard of an active forced-K cell.
  Shards wait for their turn on the shared `manifest.json`, so later shards append a
  `rerecordings` entry instead of racing the first.
- `finalize_generic.sh` (DeepSeek) / `finalize_opus.sh` (Opus 5) —
  `OUTDIR DATASET LIMIT TAG MERGE_KEY idx:jobid:KEY ...`: as each shard job exits (detected
  from `$TASK_OUTPUT_DIR/<jobid>.output`), re-runs that shard's error records on its key, in
  parallel; then keeps the sharded manifest as `manifest_shards.json` and runs one
  unsharded `--skip-existing` pass, so the cell ends as one standard full run.
- `build_examples.py` — extracts the forced-K vs random-K examples behind the
  "Queries vs random draws" page.

All shell scripts are bash: zsh does not word-split an unquoted `$ARGS`, which once broke a
finalizer. Arguments are passed as arrays.
