#!/usr/bin/env bash
# Tonight's baseline: the passive/active contrast across three model families,
# on one contaminated pool and one private one.
#
# Sequential within a provider (keeps each vendor's rate limit to itself),
# parallel across providers. --skip-existing defaults on, so re-running this
# after an interruption resumes rather than repeats.
#
#   bash scripts/overnight_baseline.sh 2>&1 | tee experiments/runs/overnight.log
#
# Needs OPENAI_API_KEY and OPENROUTER_API_KEY (both are in the SFI conda env).

set -u
cd "$(dirname "$0")/.." || exit 1
export PYTHONPATH="$PWD"

EFFORT="${EFFORT:-medium}"   # frozen for every arm; see notes in the plan
SEED="${SEED:-0}"
ARC_N="${ARC_N:-100}"        # first N of the pinned ARC-AGI-1 ordering
RUNS=experiments/runs
mkdir -p "$RUNS"

run_family () {
  local tag="$1"; shift
  local model_args=("$@")

  for spec in "arc --limit $ARC_N --offset 0" "parc --limit 50 --offset 0"; do
    set -- $spec
    local pool="$1"; shift

    echo "[$tag/$pool] active ..."
    python -m pipelines.run_active_arc_batch \
      --dataset "$pool" "$@" --seed "$SEED" \
      "${model_args[@]}" --reasoning-effort "$EFFORT" \
      --out-dir "$RUNS/sci_${pool}_${tag}_s${SEED}" \
      >> "$RUNS/sci_${pool}_${tag}_s${SEED}.log" 2>&1

    echo "[$tag/$pool] static ..."
    python -m pipelines.run_static_batch \
      --dataset "$pool" "$@" \
      "${model_args[@]}" --reasoning-effort "$EFFORT" \
      --out-dir "$RUNS/static_${pool}_${tag}" \
      >> "$RUNS/static_${pool}_${tag}.log" 2>&1
  done
  echo "[$tag] done"
}

run_family luna &
run_family sonnet --model anthropic/claude-sonnet-4.5 &
run_family gemini --model google/gemini-2.5-flash &
wait
echo "all families done"
