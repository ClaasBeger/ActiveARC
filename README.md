# ActiveARC

Interactive **query → test** trials over ARC-style tasks: explore with a verifier-backed oracle, then solve a held-out test input. The Streamlit UI lives in `interface/active_arc_app.py`.

## Quick start

```bash
pip install -r requirements.txt
streamlit run interface/active_arc_app.py
```

Pass app flags after `--` (Streamlit does not recognize them otherwise). Flags are combinable:

```bash
# One free training pair is shown at start by default (no query cost); disable with:
streamlit run interface/active_arc_app.py -- --no-hot-start

# Randomly corrupt query outputs (default p=0.12; clamped to 0.05–0.20)
streamlit run interface/active_arc_app.py -- --noisy-science
streamlit run interface/active_arc_app.py -- --noisy-science --noise-probability 0.15

# Wrong test answer sends you back to exploration (+10 query count)
streamlit run interface/active_arc_app.py -- --re-trials

# Fixed RNG for task/verifier selection
streamlit run interface/active_arc_app.py -- --seed 42

# Pin a specific ARC task (needs a validated verifier + ARC-GEN dynamic pair)
streamlit run interface/active_arc_app.py -- --task-id 8eb1be9a --seed 42

# Combine features
streamlit run interface/active_arc_app.py -- --hot-start --noisy-science --re-trials --seed 42
```

Legacy single-feature alias: `--mode hot_start` (same as `--hot-start`; OR-combined with the flags above).

For the pixel grid editor, build the frontend once:

```bash
cd interface/arc_grid_component/frontend && npm install && npm run build
```

## Experimentation

ARC task **`8eb1be9a`** is a good example to try when experimenting with the interface and modes.

## External ARC editor (`external/arc-app`)

The optional Node editor under `external/arc-app` needs a MongoDB Atlas URI. Credentials are **not** stored in source; each developer keeps a local `external/arc-app/.env` (gitignored):

```bash
cd external/arc-app
cp .env.example .env
# set MONGODB_URI=... (ask a teammate / project lead for the shared URI)
npm install
npm run build && npm start
```

See [`external/arc-app/README.md`](external/arc-app/README.md) for full setup.

## ConceptARC dataset

ActiveARC can also run trials over **ConceptARC** DSL programs, kept fully separate
from the ARC-AGI pool. Choose the pool with `--dataset` (or the **Dataset** selector
in the sidebar); ARC-AGI stays the default:

```bash
# Random ConceptARC program (from the exported catalog)
streamlit run interface/active_arc_app.py -- --dataset conceptarc

# A specific ConceptARC program (ids are <concept>/<task>, e.g. count/count11, copy/copy12)
streamlit run interface/active_arc_app.py -- --dataset conceptarc --task-id count/count11

# Sample a brand-new DSL task family online (ConceptARC-GEN layer 3)
streamlit run interface/active_arc_app.py -- --dataset conceptarc --task-id sample
streamlit run interface/active_arc_app.py -- --dataset conceptarc --task-id count/sample
# equivalent:
streamlit run interface/active_arc_app.py -- --dataset conceptarc --sample-family
```

The same `--dataset conceptarc` flag works for the headless agent runner
(`pipelines/run_active_arc_agent.py`) and `create_trial_session(..., dataset="conceptarc")`.
Pass `sample_family=True` or a `task_id` of `sample` / `<concept>/sample` to invent a
new program at trial time; optional `persist_sampled_family=True` writes it into the
exported catalog.

Exported programs live under `external/conceptarc/programs/<concept>/<task>.json`
(16 concepts × 15 families = 240 programs: official 1–10 plus generated 11–15).
Official tasks reuse the ConceptARC corpus examples; generated families ship three
freshly generated examples plus a held-out test pool. The live query verifier and
the dynamic test generator are rebuilt from each program via the `conceptarc_gen`
package, imported from `CONCEPTARC_GEN_ROOT` (default: the sibling
`../../ConceptARC-Generator/ConceptARC-GEN` checkout). ConceptARC requires Python 3.12
and the ConceptARC-GEN repo's pinned `external/ARC-GEN` submodule (for the `common`
module).

To (re)generate the exported programs, run from the ConceptARC-GEN repo root:

```bash
# Optional: invent more families (writes output/conceptarc_specs/<concept>/<task>11+.json)
python conceptarc_gen_tasks.py --concept_name count --num_task_families 5 --seed 42

PYTHONPATH="$(pwd)/external/ARC-GEN" .venv/bin/python export_to_activearc.py \
    --out /path/to/ActiveARC/external/conceptarc/programs
```

## Slippage pair search (ARC-AGI-1)

Offline search for **narrow vs broad** verifier pairs used by slippage experiments
(no UI yet). Broad = ``re_arc``; narrow = golf/custom slots that still pass the
ARC-GEN distribution but fail on a majority of RE-ARC samples:

```bash
python -m pipelines.find_slippage_pairs \
    --out experiments/slippage/slippage_pairs.json \
    --max-re-arc-pairs 100
```

Results land in `experiments/slippage/slippage_pairs.json`.

## P-ARC dataset

ActiveARC can also run trials over **P-ARC** (`t1`–`t50`), kept separate from
ARC-AGI and ConceptARC:

```bash
# Random P-ARC task
streamlit run interface/active_arc_app.py -- --dataset parc

# Pin a task (ids: test2_t1 … test2_t50, or short forms t1 … t50)
streamlit run interface/active_arc_app.py -- --dataset parc --task-id test2_t1
```

Each task uses its own `verifier.py` / `generator.py`, with the committed 50-pair
stable pool as a fallback when live generation fails. Data is resolved from
`PARC_ROOT` / `TEST2_DIR`, then `external/Test2`, then the sibling checkout
`../../PotARCin/PotARCin/Test2`.
