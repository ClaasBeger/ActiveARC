# ActiveARC

Interactive **query → test** trials over ARC-style tasks: explore with a verifier-backed oracle, then solve a held-out test input. The Streamlit UI lives in `interface/active_arc_app.py`.

## Quick start

```bash
pip install -r requirements.txt
streamlit run interface/active_arc_app.py
```

Pass app flags after `--` (Streamlit does not recognize them otherwise). Flags are combinable:

```bash
# One free training pair shown at start (no query cost)
streamlit run interface/active_arc_app.py -- --hot-start

# Randomly corrupt query outputs (default p=0.12; clamped to 0.05–0.20)
streamlit run interface/active_arc_app.py -- --noisy-science
streamlit run interface/active_arc_app.py -- --noisy-science --noise-probability 0.15

# Wrong test answer sends you back to exploration (+10 query count)
streamlit run interface/active_arc_app.py -- --re-trials

# Fixed RNG for task/verifier selection
streamlit run interface/active_arc_app.py -- --seed 42

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
