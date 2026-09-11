#!/usr/bin/env python3
"""Rebuild compact LARC / MARC2 NL-rule lookups under ``external/nl_rules``.

Downloads LARC summary CSVs and MARC2 HuggingFace parquet, then keeps:

* ARC-AGI-1: LARC descriptions with ≥1 independent builder success.
* ARC-AGI-2 train: MARC2 descriptions with ``validated==1``.
"""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

OUT_DIR = ROOT_DIR / "external" / "nl_rules"

LARC_BASE = "https://raw.githubusercontent.com/samacqua/LARC/main/dataset/summary"
MARC2_DESC = (
    "https://huggingface.co/datasets/bertybaums/marc2/resolve/main/"
    "descriptions/train.parquet"
)
MARC2_TASKS = (
    "https://huggingface.co/datasets/bertybaums/marc2/resolve/main/tasks/train.parquet"
)


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _compose(*parts: object) -> str:
    chunks = [str(p).strip() for p in parts if p and str(p).strip()]
    return "\n\n".join(chunks)


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as resp, dest.open("wb") as f:
        f.write(resp.read())


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_larc(src: Path) -> dict:
    tasks = {r["task_id"]: r for r in _read_csv(src / "task.csv")}
    descs = {r["description_id"]: r for r in _read_csv(src / "description.csv")}
    builds = {r["build_id"]: r for r in _read_csv(src / "build.csv")}
    joins = _read_csv(src / "join.csv")
    succ: Counter[str] = Counter()
    for row in joins:
        build = builds.get(row["build_id"])
        if build and _truthy(build["is_success"]):
            succ[row["description_id"]] += 1
    by_task: dict[str, list[str]] = defaultdict(list)
    for row in joins:
        did = row["description_id"]
        if succ[did] >= 1:
            by_task[row["task_id"]].append(did)
    rules: dict[str, str] = {}
    for tid, dids in by_task.items():
        uniq = sorted(
            set(dids),
            key=lambda d: (
                -succ[d],
                -float(descs[d].get("confidence") or 0),
                int(float(descs[d].get("num_verification_attempts") or 99)),
                d,
            ),
        )
        desc = descs[uniq[0]]
        name = tasks[tid]["task_name"].replace(".json", "").strip().lower()
        text = _compose(
            desc.get("description_input") or "",
            desc.get("description_output_grid_size") or "",
            desc.get("description_output") or "",
        )
        if name and text:
            rules[name] = text
    return {
        "_meta": {
            "source": "https://github.com/samacqua/LARC",
            "files": "dataset/summary/{task,description,build,join}.csv",
            "filter": (
                "Keep a description only if at least one independent builder "
                "reconstructed the test output from the description alone "
                "(build.is_success). Among those, pick the description with the "
                "most successful builds, then highest describer confidence."
            ),
            "n_tasks": len(rules),
        },
        "rules": dict(sorted(rules.items())),
    }


def build_marc2(desc_path: Path, tasks_path: Path) -> dict:
    import pandas as pd

    desc = pd.read_parquet(desc_path)
    tasks = pd.read_parquet(tasks_path)
    merged = desc.merge(tasks, on="task_id")
    kept = merged[(merged["validated"] == 1) & (merged["source"] == "training")]
    rules: dict[str, str] = {}
    for _, row in kept.iterrows():
        name = str(row["arc_name"]).replace(".json", "").strip().lower()
        text = _compose(
            row["see_description"],
            row["do_description"],
            row["grid_description"],
        )
        if name and text:
            rules[name] = text
    return {
        "_meta": {
            "source": "https://huggingface.co/datasets/bertybaums/marc2",
            "code": "https://github.com/bertybaums/marc2",
            "filter": (
                "ARC-AGI-2 training split only; descriptions.validated==1 "
                "(passed independent description-only solver validation)."
            ),
            "n_tasks": len(rules),
        },
        "rules": dict(sorted(rules.items())),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        larc_dir = tmp_path / "larc"
        for name in ("task.csv", "description.csv", "build.csv", "join.csv"):
            print(f"download LARC {name}", flush=True)
            _download(f"{LARC_BASE}/{name}", larc_dir / name)
        larc = build_larc(larc_dir)
        (OUT_DIR / "larc_arc_agi_1.json").write_text(
            json.dumps(larc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"LARC {larc['_meta']['n_tasks']} tasks", flush=True)

        print("download MARC2 parquet", flush=True)
        desc_pq = tmp_path / "descriptions.parquet"
        tasks_pq = tmp_path / "tasks.parquet"
        _download(MARC2_DESC, desc_pq)
        _download(MARC2_TASKS, tasks_pq)
        marc = build_marc2(desc_pq, tasks_pq)
        (OUT_DIR / "marc2_arc_agi_2.json").write_text(
            json.dumps(marc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"MARC2 {marc['_meta']['n_tasks']} tasks", flush=True)


if __name__ == "__main__":
    main()
