# ActiveARC

Interactive **query → test** trials over ARC-style tasks: explore with a verifier-backed oracle, then solve a held-out test input. The Streamlit UI lives in `interface/active_arc_app.py`.

## Quick start

```bash
pip install -r requirements.txt
streamlit run interface/active_arc_app.py
```

Optional features (combinable): `--hot-start`, `--noisy-science`, `--re-trials`, plus `--seed` and `--noise-probability` (for noisy queries). Legacy `--mode` is still supported as a single-feature alias.

For the pixel grid editor, build the frontend once:

```bash
cd interface/arc_grid_component/frontend && npm install && npm run build
```

## Experimentation

ARC task **`8eb1be9a`** is a good example to try when experimenting with the interface and modes.
