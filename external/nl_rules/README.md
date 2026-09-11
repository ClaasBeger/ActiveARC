# Natural-language rules for Inverse Query

Compact lookups used as the teacher’s `natural_language_rule` for ARC-AGI-1/2.

| File | Source | Filter |
| --- | --- | --- |
| `larc_arc_agi_1.json` | [samacqua/LARC](https://github.com/samacqua/LARC) | Independent builder reconstructed the test output from the description alone |
| `marc2_arc_agi_2.json` | [bertybaums/marc2](https://huggingface.co/datasets/bertybaums/marc2) | ARC-AGI-2 **training** descriptions with `validated==1` (description-only solver) |

Rebuild:

```bash
python -m pipelines.build_nl_rule_lookups
```
