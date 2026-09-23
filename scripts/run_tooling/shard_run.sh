#!/bin/bash
# usage: shard_run.sh OUTDIR DATASET LIMIT TAG SHARD_IDX KEYVAR
# Waits until the shared manifest records SHARD_IDX earlier entries (base + rerecordings) so
# concurrent shards never race on manifest.json, then runs its task list.
set -u
OUT=$1; DS=$2; LIM=$3; TAG=$4; K=$5; KEY=$6
J="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$J/../.."
entries() { python3 -c "import json,sys
try: m=json.load(open(sys.argv[1])); print(1+len(m.get('rerecordings',[])))
except Exception: print(0)" "$OUT/manifest.json"; }
until [ "$(entries)" -ge "$K" ]; do sleep 2; done
read -r -a TIDS < "$J/shards/${TAG}_shard${K}.args"
exec conda run --no-capture-output -n jagEval bash "$J/with_key.sh" "$KEY" python -u -m pipelines.run_active_arc_batch \
  --dataset "$DS" --limit "$LIM" --offset 0 --seed 0 --test-source both --forced-k auto \
  --model deepseek/deepseek-v4.1-flash --provider openrouter --backend chat --reasoning-effort low \
  --out-dir "$OUT" --skip-existing "${TIDS[@]}"
