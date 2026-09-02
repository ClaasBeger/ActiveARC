# arc-agi2-solutions

**Verified Python programs for a subset of [ARC-AGI-2](https://github.com/arcprize/ARC-AGI-2) training tasks, with a focus on executable problem–program pairs for LLM program synthesis.**

[ARC-AGI-2](https://github.com/arcprize/ARC-AGI-2) consists of abstract grid-transformation problems. Given input/output demonstrations, a solver must infer a transformation that maps a new input grid to the correct output.

This repository represents those inferred transformations as **executable Python programs** and verifies them against the available ARC-AGI-2 examples.

> **Core idea:** `ARC task → Python transformation program`

The longer-term motivation is to explore whether such problem–program pairs can be used as data for **LLM fine-tuning and program-synthesis experiments**.

## What is included

| File | Solvers | Origin |
|------|---------|--------|
| `our_task_solutions.py` | **222** | Manually written solutions — **main contribution** |
| `barc_task_solutions.py` | **158** | Converted [BARC seed](https://github.com/xu3kev/BARC/tree/master/seeds) programs |
| `llm_task_solutions.py` | **37** | Additional LLM-assisted solutions |

There are **383 unique ARC-AGI-2 training-task IDs out of 1,000** across the three files, with 34 IDs appearing in both `our_task_solutions.py` and `barc_task_solutions.py`.

All listed solvers are verified against their available official training and test pairs. Unsolved tasks are left unsolved rather than filled with speculative solutions.

**Important:** these programs are candidate transformations inferred from the demonstrations. They are not necessarily the true underlying ARC rules and are not claimed to generalize to unseen tasks.

## Why this repository?

Most ARC work focuses on predicting the output grid. This repository takes a complementary approach: **represent the inferred reasoning as executable code**.

This creates a collection of:

- ARC task examples
- Explicit transformation programs
- Verified input/output behavior

Such **problem–program pairs** can potentially be used to investigate:

- LLM fine-tuning for program synthesis
- Code generation for abstract reasoning
- Few-shot program induction
- Generalization of learned transformation programs

This repository is a dataset/code collection for these experiments, **not an LLM training framework**.

## Example

Each solution follows a common format:

```python
def solve_<task_id>(input_grid):
    """Transformation inferred from the demonstrations."""
    input_grid = np.array(input_grid)
    ...
    return output_grid
```

A solution can then be executed directly:

```python
from our_task_solutions import solve_c9e6f938

output_grid = solve_c9e6f938(input_grid)
```

The repository also includes notebook-based visualizations comparing:

**Input → Predicted Output → Ground Truth**

## Repository structure

| File | Description |
|------|-------------|
| `our_task_solutions.py` | 222 manually written `solve_<task_id>` functions. **Main contribution.** |
| `barc_task_solutions.py` | 158 [BARC seed](https://github.com/xu3kev/BARC/tree/master/seeds) conversions using the same format. |
| `llm_task_solutions.py` | 37 additional verified solutions. |
| `grid_utils.py` | Shared grid utilities. |
| `barc_common.py` | BARC grid utilities adapted for ARC conventions. |
| `validate.py` | Verifies all available solutions against official ARC-AGI-2 examples. |
| `validate_solutions.ipynb` | Validation, visualization, and solution comparison notebook. |
| `LICENSE` | License for original code. |
| `NOTICE` | Attribution and licensing information. |
| `CITATION.cff` | Citation metadata. |

## Verification

Run the complete validation from the repository root:

```bash
python validate.py
```

Or run all cells in:

```text
validate_solutions.ipynb
```

The validation checks that each solver reproduces the expected output for every available official example associated with that task.

## Setup

Requires Python 3.9+, NumPy, SciPy, and Matplotlib.

```bash
pip install -r requirements.txt
git clone https://github.com/arcprize/ARC-AGI-2.git
```

The official ARC-AGI-2 dataset is **not redistributed** in this repository. The cloned `ARC-AGI-2/` directory should be located at the repository root and is gitignored.

For the notebook:

```bash
pip install notebook
```

## BARC conversions

Solutions are converted from the [BARC seed programs](https://github.com/xu3kev/BARC/tree/master/seeds).

BARC seeds that use `[x, y]` indexing are wrapped with `_barc_xy` to match the official ARC `[row, col]` convention.

Alternate `_Kevin.py` seeds and ConceptARC examples were not converted. Two BARC seed IDs (`0dfd9992`, `a3df8b1e`) are not present in ARC-AGI-2 and were therefore omitted.

## License and attribution

Original code in this repository is released under the MIT License. See [`LICENSE`](LICENSE).

`barc_task_solutions.py` and `barc_common.py` contain conversions of BARC seed code. The BARC repository does not currently publish a LICENSE file; those portions remain attributed to their original authors. See [`NOTICE`](NOTICE).

ARC-AGI-2 task data is Apache-2.0 licensed and is **not redistributed** here.

## References

- [ARC-AGI-2](https://github.com/arcprize/ARC-AGI-2)
- [BARC](https://github.com/xu3kev/BARC) — seed programs
- François Chollet, [On the Measure of Intelligence](https://arxiv.org/abs/1911.01547)
- Wen-Ding Li et al., [Combining Induction and Transduction for Abstract Reasoning](https://arxiv.org/abs/2411.02272)

## Citation

If you use this repository in research or build on its solutions, please cite this repository using the metadata in [`CITATION.cff`](CITATION.cff).
