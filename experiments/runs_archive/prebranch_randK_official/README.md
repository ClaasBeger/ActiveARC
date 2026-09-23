# Pre-branch random-K runs, official item (archived 2026-09-17)

The twelve random-K cells as they were before the branched rewrite. Kept for
provenance; **do not mix them with anything under `experiments/runs/`.**

Two reasons they are not comparable with the current arms:

1. **Different answering structure.** These came from the old `predict()` path,
   which put the training pairs and the test input in one message. The current
   `study_and_answer()` spends a dedicated study turn on the pairs alone ("Work
   out the transformation rule they share") before any test grid is shown, then
   forks per held-out item. `static_*_br` and `sciK_*_b` all use the new path.

2. **Different evidence.** They predate `cb91cba0`, which passes the held-out
   inputs to `_generator_pairs` as exclusions. Any non-empty exclusion changes
   the sampler's RNG path, so the drawn pairs differ even where nothing was
   excludable. These runs scored the *official* item, which the leak barely
   touched (0% on arc, 2% on arc2), so they are stale rather than contaminated.

Their replacements are being written to the same directory names under
`experiments/runs/`, with `--test-source official` and current code.

69 MB, untracked -- as they were in `experiments/runs/`.

See the `randk-evidence-leak` project memory for the contamination story, which
concerned the *sampled* item and the `randK_*_samp` directories, not these.
