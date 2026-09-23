#!/bin/bash
# usage: finalize_generic.sh OUTDIR DATASET LIMIT TAG MERGE_KEY  idx:taskid:KEY ...
# Per-shard error reruns in parallel as each shard exits, then one merged full pass.
set -u
OUT=$1; DS=$2; LIM=$3; TAG=$4; MKEY=$5; shift 5
D="${TASK_OUTPUT_DIR:?set TASK_OUTPUT_DIR to the directory holding the shard job logs}"
J="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$J/../.."
ARGS=(--dataset "$DS" --limit "$LIM" --offset 0 --seed 0 --test-source both --forced-k auto
      --model deepseek/deepseek-v4.1-flash --provider openrouter --backend chat --reasoning-effort low --out-dir "$OUT" --skip-existing)
one() {
  IFS=: read -r k tid key <<< "$1"
  until grep -q 'exited with code' "$D/$tid.output"; do sleep 60; done
  echo "[finalize $TAG] shard $k exited; re-running its error records on $key ($(date +%H:%M))"
  read -r -a TIDS < "$J/shards/${TAG}_shard$k.args"
  conda run --no-capture-output -n jagEval bash "$J/with_key.sh" "$key" python -u -m pipelines.run_active_arc_batch "${ARGS[@]}" "${TIDS[@]}"
  echo "[finalize $TAG] shard $k rerun done ($(date +%H:%M))"
}
for spec in "$@"; do one "$spec" & done
wait
echo "[finalize $TAG] all shard reruns done ($(date +%H:%M))"
[ -e "$OUT/manifest_shards.json" ] || cp -p "$OUT/manifest.json" "$OUT/manifest_shards.json"
conda run --no-capture-output -n jagEval bash "$J/with_key.sh" "$MKEY" python -u -m pipelines.run_active_arc_batch "${ARGS[@]}"
echo "[finalize $TAG] merged pass done ($(date +%H:%M))"
