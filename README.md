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

## ConceptARC dataset

ActiveARC can also run trials over **ConceptARC** DSL programs, kept fully separate
from the ARC-AGI pool. Choose the pool with `--dataset` (or the **Dataset** selector
in the sidebar); ARC-AGI stays the default:

```bash
# Random ConceptARC program
streamlit run interface/active_arc_app.py -- --dataset conceptarc

# A specific ConceptARC program (ids are <concept>/<task>, e.g. count/count11, copy/copy12)
streamlit run interface/active_arc_app.py -- --dataset conceptarc --task-id count/count11
```

The same `--dataset conceptarc` flag works for the headless agent runner
(`pipelines/run_active_arc_agent.py`) and `create_trial_session(..., dataset="conceptarc")`.

Exported programs live under `external/conceptarc/programs/<concept>/<task>.json`
(five concepts: count, center, insideoutside, abovebelow, copy). Official tasks
1–10 reuse the ConceptARC corpus examples; generated families >10 ship three
freshly generated examples plus a held-out test pool. The live query verifier and
the dynamic test generator are rebuilt from each program via the `conceptarc_gen`
package, imported from `CONCEPTARC_GEN_ROOT` (default: the sibling
`../../ConceptARC-Generator/ConceptARC-GEN` checkout). ConceptARC requires Python 3.12
and the ConceptARC-GEN repo's pinned `external/ARC-GEN` submodule (for the `common`
module).

To (re)generate the exported programs, run from the ConceptARC-GEN repo root:

```bash
PYTHONPATH="$(pwd)/external/ARC-GEN" .venv/bin/python export_to_activearc.py \
    --out /path/to/ActiveARC/external/conceptarc/programs
```
