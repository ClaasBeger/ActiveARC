DO NOT USE THE PER-ITEM RESULTS IN THIS RUN.

Every trial here with more than one held-out test item was shown all of them in
one message and answered them in a single call. Each answer was therefore given
having seen the other items' input grids, so `test_item_correct` entries are not
independent measurements.

What that rules out:
  - comparing per-item accuracy against the static arm, which answers one test
    item at a time in a fresh context;
  - comparing against single-item runs (anything without --test-source both);
  - reading the official-vs-sampled difference as a property of the items.

What still holds:
  - the all-items-correct `correct` field remains a valid joint measure;
  - trials with only one test item are unaffected.

Re-run with the branched test phase (each item answered on its own fork of the
exploration conversation) to obtain independent per-item results.

Affected trials: 49 of 50
Flagged at: 2026-09-16T03:30:05.661055+00:00
