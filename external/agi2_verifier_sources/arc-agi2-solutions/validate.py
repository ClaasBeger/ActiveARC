"""Verify every solve_* function against official ARC-AGI-2 train and test pairs."""

import glob
import json
import re
import sys
from pathlib import Path

import barc_task_solutions
import llm_task_solutions
import our_task_solutions

sys.setrecursionlimit(20000)

REPO_DIR = Path(__file__).resolve().parent
DATASET_DIR = REPO_DIR / "ARC-AGI-2"


def load_training_tasks(dataset_dir):
    tasks = {}
    for path in glob.glob(str(Path(dataset_dir) / "data" / "training" / "*.json")):
        with open(path) as f:
            tasks[Path(path).stem] = json.load(f)
    return tasks


def list_solved_task_ids(solutions_path):
    return re.findall(r"^def solve_(\w+)\(", Path(solutions_path).read_text(), re.MULTILINE)


def validate_module(module, task_ids, tasks):
    failed = []
    for i, task_id in enumerate(task_ids):
        task = tasks[task_id]
        solve_fn = getattr(module, f"solve_{task_id}")
        passed_train = our_task_solutions.verify_solution_outputs(task, "train", solve_fn)
        passed_test = our_task_solutions.verify_solution_outputs(task, "test", solve_fn)
        status = "PASS" if passed_train and passed_test else "FAIL"
        print(f"({i + 1:3d}/{len(task_ids)}) {task_id}  {status}  train={passed_train}  test={passed_test}")
        if not (passed_train and passed_test):
            failed.append(task_id)
    if failed:
        print("Failed:", ", ".join(failed))
        return False
    print(f"\nAll {len(task_ids)} solutions validated successfully.")
    return True


def main():
    if not (DATASET_DIR / "data" / "training").is_dir():
        print(
            f"ARC-AGI-2 dataset not found at {DATASET_DIR}\n"
            "Clone it from the repository root:\n"
            "  git clone https://github.com/arcprize/ARC-AGI-2.git",
            file=sys.stderr,
        )
        return 1

    tasks = load_training_tasks(DATASET_DIR)
    print(f"Loaded {len(tasks)} training tasks.\n")

    modules = [
        ("our_task_solutions.py", our_task_solutions),
        ("barc_task_solutions.py", barc_task_solutions),
        ("llm_task_solutions.py", llm_task_solutions),
    ]
    ok = True
    for filename, module in modules:
        task_ids = list_solved_task_ids(REPO_DIR / filename)
        print(f"Found {len(task_ids)} solution functions in {filename}")
        ok = validate_module(module, task_ids, tasks) and ok
        print()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
