# ARC-AGI-2 standalone verifiers

Candidates for the 500 ARC-GEN V2 task IDs, imported from:

- `GitMonsters/SOLVED-562-verified`
- `ArunSehrawat/arc-agi2-solutions`
- `epang080516/arc_agi` (`saved_library_1000.pkl`, CT Pang)

## Layout

- `candidates/` — normalized `verify(input_grid) -> output_grid` modules + `.meta.json` provenance
- `valid/` — candidates that passed **all** official train/test pairs and **250** ARC-GEN dynamic pairs
- `logs/` — alignment, validation JSONL, coverage
- `candidates_index.json`, `import_summary.json`

## Re-run

```bash
python -m scripts.import_agi2_verifiers --workers 8
python -m scripts.import_agi2_verifiers --collect-only
python -m scripts.import_agi2_verifiers --validate-only --workers 8
```

CT Pang programs are aligned monotonically to lex-sorted ARC-AGI-2 training IDs via official-pair anchors (never by order alone). Rejected mappings are in `logs/ct_pang_alignment.json`.
