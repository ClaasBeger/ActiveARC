"""Isolated-process validation of normalized verifier candidates."""

from __future__ import annotations

import importlib.util
import json
import logging
import multiprocessing as mp
import signal
import shutil
import traceback
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FuturesTimeout, as_completed
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .grid_utils import deep_copy_grid, grids_equal, load_official_pairs, to_grid
from .paths import ARC_ORIGINAL, CANDIDATES, LOGS, ROOT, VALID

logger = logging.getLogger(__name__)

N_DYNAMIC = 250
GENERATION_TIMEOUT_S = 10.0
TIMEOUT_PASS1 = 5.0
TIMEOUT_PASS2 = 60.0


@dataclass
class CaseResult:
    case_id: str
    status: str
    detail: str = ""


@dataclass
class CandidateResult:
    candidate_id: str
    task_id: str
    source: str
    original_path: str
    license: str
    relative_path: str
    status: str
    official_attempted: int = 0
    official_passed: int = 0
    dynamic_attempted: int = 0
    dynamic_passed: int = 0
    dynamic_generator_failures: int = 0
    timeouts: int = 0
    cases: List[CaseResult] = field(default_factory=list)
    pass_number: int = 1


class _CaseTimeout(Exception):
    pass


def _alarm_handler(signum, frame):  # noqa: ARG001
    raise _CaseTimeout("case timeout")


def _load_verify_fn(path: Path):
    import contextlib
    import io
    import os

    spec = importlib.util.spec_from_file_location(f"agi2_cand_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    # Many GitMonsters solvers print/self-test at import when guards are imperfect.
    with open(os.devnull, "w") as devnull, contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
        spec.loader.exec_module(mod)
    fn = getattr(mod, "verify", None)
    if not callable(fn):
        raise AttributeError("module has no verify()")
    return fn


def _run_one_case(fn, case_id: str, inp, exp) -> CaseResult:
    working = deep_copy_grid(inp)
    original = deep_copy_grid(inp)
    try:
        got = fn(working)
    except _CaseTimeout:
        raise
    except Exception as e:
        return CaseResult(case_id, "exception", f"{type(e).__name__}: {e}")
    if working != original:
        return CaseResult(case_id, "input_mutation", "verify mutated input_grid in place")
    if to_grid(got) is None:
        return CaseResult(case_id, "malformed_output", f"type={type(got).__name__}")
    if not grids_equal(got, exp):
        g = to_grid(got)
        detail = (
            f"got_shape={len(g)}x{len(g[0]) if g else 0} "
            f"exp_shape={len(exp)}x{len(exp[0]) if exp else 0}"
        )
        return CaseResult(case_id, "incorrect_output", detail)
    return CaseResult(case_id, "pass")


def _run_one_case_alarm(fn, case_id: str, inp, exp, timeout_s: float) -> CaseResult:
    if timeout_s <= 0 or not hasattr(signal, "SIGALRM"):
        return _run_one_case(fn, case_id, inp, exp)
    old = signal.signal(signal.SIGALRM, _alarm_handler)
    try:
        signal.setitimer(signal.ITIMER_REAL, timeout_s)
        try:
            return _run_one_case(fn, case_id, inp, exp)
        except _CaseTimeout:
            return CaseResult(case_id, "timeout", f"exceeded {timeout_s}s")
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


_DYNAMIC_CACHE_DIR = LOGS / "dynamic_cache"


def _generate_dynamic_pairs(task_id: str, n: int = N_DYNAMIC) -> Tuple[List[Tuple], int]:
    import sys
    import random as pyrandom

    _DYNAMIC_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = _DYNAMIC_CACHE_DIR / f"{task_id}_{n}.json"
    if cache_path.is_file():
        blob = json.loads(cache_path.read_text())
        pairs = [
            (cid, to_grid(inp), to_grid(out))
            for cid, inp, out in blob["pairs"]
        ]
        # Re-normalize in case of older cache
        pairs = [(c, i, o) for c, i, o in pairs if i is not None and o is not None]
        if len(pairs) >= n:
            return pairs[:n], int(blob.get("generator_failures", 0))

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from framework.tasks.arc_dataset import _arc_gen_id_to_task_num_and_generator

    lookup = _arc_gen_id_to_task_num_and_generator(task_id)
    if lookup is None:
        raise RuntimeError(f"no ARC-GEN generator for {task_id}")
    _, generator = lookup

    pairs: List[Tuple] = []
    seed = 0
    failures = 0
    max_seed = n * 50 + 1000
    while len(pairs) < n and seed < max_seed:
        state = pyrandom.getstate()
        try:
            pyrandom.seed(seed)
            if hasattr(signal, "SIGALRM"):
                old = signal.signal(signal.SIGALRM, _alarm_handler)
                try:
                    signal.setitimer(signal.ITIMER_REAL, GENERATION_TIMEOUT_S)
                    example = generator()
                except _CaseTimeout:
                    failures += 1
                    seed += 1
                    continue
                finally:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    signal.signal(signal.SIGALRM, old)
            else:
                example = generator()
            inp = to_grid(example["input"])
            out = to_grid(example["output"])
            if inp is None or out is None:
                failures += 1
            else:
                pairs.append((f"dynamic[seed={seed}]", inp, out))
        except _CaseTimeout:
            failures += 1
        except Exception:
            failures += 1
        finally:
            pyrandom.setstate(state)
        seed += 1
    if len(pairs) < n:
        raise RuntimeError(
            f"only generated {len(pairs)}/{n} dynamic pairs after {seed} seeds "
            f"({failures} generator failures)"
        )
    cache_path.write_text(
        json.dumps(
            {
                "task_id": task_id,
                "n": n,
                "generator_failures": failures,
                "pairs": [[cid, inp, out] for cid, inp, out in pairs],
            }
        )
    )
    return pairs, failures


def _atomic_write_json(path: Path, payload: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload))
    tmp.replace(path)


def _empty_result(meta: dict, pass_number: int) -> CandidateResult:
    return CandidateResult(
        candidate_id=meta["candidate_id"],
        task_id=meta["task_id"],
        source=meta["source"],
        original_path=meta["original_path"],
        license=meta["license"],
        relative_path=meta["relative_path"],
        status="invalid",
        pass_number=pass_number,
    )


def validate_candidate_payload(payload: dict) -> dict:
    """Worker entrypoint — one candidate, isolated process."""
    meta = json.loads(Path(payload["meta_path"]).read_text())
    timeout_s = float(payload["timeout_s"])
    pass_number = int(payload["pass_number"])
    result = _empty_result(meta, pass_number)
    py_path = CANDIDATES / meta["relative_path"]
    task_id = meta["task_id"]

    try:
        fn = _load_verify_fn(py_path)
    except Exception as e:
        result.cases.append(
            CaseResult("load", "exception", f"{type(e).__name__}: {e}\n{traceback.format_exc()[:800]}")
        )
        return asdict(result)

    task_json = json.loads((ARC_ORIGINAL / f"{task_id}.json").read_text())
    official = load_official_pairs(task_json)
    cases: List[Tuple[str, Any, Any]] = [
        (f"{split}[{i}]", inp, exp) for split, i, inp, exp in official
    ]
    try:
        dynamic, gen_fails = _generate_dynamic_pairs(task_id, N_DYNAMIC)
        result.dynamic_generator_failures = gen_fails
        cases.extend(dynamic)
    except Exception as e:
        result.cases.append(
            CaseResult("dynamic_generate", "generator_failure", f"{type(e).__name__}: {e}")
        )
        return asdict(result)

    failure_cases: List[CaseResult] = []
    for case_id, inp, exp in cases:
        is_official = not str(case_id).startswith("dynamic")
        if is_official:
            result.official_attempted += 1
        else:
            result.dynamic_attempted += 1
        cr = _run_one_case_alarm(fn, case_id, inp, exp, timeout_s)
        if cr.status == "pass":
            if is_official:
                result.official_passed += 1
            else:
                result.dynamic_passed += 1
        elif cr.status == "timeout":
            result.timeouts += 1
            failure_cases.append(cr)
        else:
            failure_cases.append(cr)
            result.cases = failure_cases
            result.status = "invalid"
            return asdict(result)

    result.cases = failure_cases
    if result.timeouts > 0:
        # Every completed case passed; only timeouts remain.
        result.status = "pending_timeout"
    elif (
        result.official_passed == result.official_attempted
        and result.dynamic_passed == N_DYNAMIC
        and result.official_attempted > 0
    ):
        result.status = "valid"
        result.cases = []
    else:
        result.status = "invalid"
    return asdict(result)


def _official_prefilter(meta_path: Path, timeout_s: float = TIMEOUT_PASS1) -> Optional[dict]:
    """Return an invalid CandidateResult dict if official pairs already fail; else None."""
    meta = json.loads(meta_path.read_text())
    result = _empty_result(meta, 1)
    py_path = CANDIDATES / meta["relative_path"]
    try:
        fn = _load_verify_fn(py_path)
    except Exception as e:
        result.cases.append(CaseResult("load", "exception", f"{type(e).__name__}: {e}"))
        return asdict(result)
    task_json = json.loads((ARC_ORIGINAL / f"{meta['task_id']}.json").read_text())
    official = load_official_pairs(task_json)
    for split, i, inp, exp in official:
        result.official_attempted += 1
        cr = _run_one_case_alarm(fn, f"{split}[{i}]", inp, exp, timeout_s)
        if cr.status == "pass":
            result.official_passed += 1
        elif cr.status == "timeout":
            # Defer to full isolated worker / second pass.
            return None
        else:
            result.cases.append(cr)
            result.status = "invalid"
            return asdict(result)
    return None


def _load_existing_results(log_path: Path) -> Dict[str, dict]:
    by_id: Dict[str, dict] = {}
    if not log_path.is_file():
        return by_id
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            cid = row.get("candidate_id")
            if cid:
                by_id[cid] = row
    return by_id


def _worker_entry(q, payload: dict) -> None:
    try:
        q.put(validate_candidate_payload(payload))
    except Exception as e:
        meta = json.loads(Path(payload["meta_path"]).read_text())
        res = asdict(_empty_result(meta, int(payload["pass_number"])))
        res["status"] = "invalid"
        res["cases"] = [asdict(CaseResult("worker", "exception", f"{type(e).__name__}: {e}"))]
        q.put(res)


def _run_one_isolated(payload: dict, overall_timeout_s: float) -> dict:
    """Run one candidate in a child process; hard-kill on overall timeout."""
    ctx = mp.get_context("spawn")
    q: mp.Queue = ctx.Queue()
    proc = ctx.Process(target=_worker_entry, args=(q, payload))
    proc.start()
    proc.join(overall_timeout_s)
    meta = json.loads(Path(payload["meta_path"]).read_text())
    if proc.is_alive():
        proc.terminate()
        proc.join(5)
        if proc.is_alive():
            proc.kill()
            proc.join(2)
        res = asdict(_empty_result(meta, int(payload["pass_number"])))
        res["status"] = "pending_timeout"
        res["timeouts"] = 1
        res["cases"] = [
            asdict(
                CaseResult(
                    "worker",
                    "timeout",
                    f"overall worker exceeded {overall_timeout_s}s (hard-killed)",
                )
            )
        ]
        return res
    try:
        return q.get_nowait()
    except Exception as e:
        res = asdict(_empty_result(meta, int(payload["pass_number"])))
        res["status"] = "invalid"
        res["cases"] = [asdict(CaseResult("worker", "exception", f"no_result: {e}"))]
        return res


def run_validation(
    meta_paths: Sequence[Path],
    *,
    workers: int = 4,
    pass_number: int = 1,
    timeout_s: float = TIMEOUT_PASS1,
    overall_timeout_s: Optional[float] = None,
    resume: bool = True,
) -> List[dict]:
    LOGS.mkdir(parents=True, exist_ok=True)
    if overall_timeout_s is None:
        # Hard cap per candidate so hung gens/solvers cannot stall the pool.
        overall_timeout_s = 120.0

    log_path = LOGS / f"validation_pass{pass_number}.jsonl"
    existing = _load_existing_results(log_path) if resume else {}
    results: List[dict] = list(existing.values())
    done_ids = set(existing)

    pending_paths: List[Path] = []
    for p in meta_paths:
        meta = json.loads(p.read_text())
        if meta["candidate_id"] in done_ids:
            continue
        if pass_number == 1:
            early = _official_prefilter(p, timeout_s=timeout_s)
            if early is not None:
                results.append(early)
                done_ids.add(early["candidate_id"])
                with open(log_path, "a") as f:
                    f.write(json.dumps(early) + "\n")
                continue
        pending_paths.append(p)

    logger.info(
        "Validation pass%d: resume=%d prefiltered_done=%d remaining=%d",
        pass_number,
        len(existing),
        len(done_ids) - len(existing),
        len(pending_paths),
    )

    payloads = [
        {
            "meta_path": str(p),
            "timeout_s": timeout_s,
            "pass_number": pass_number,
        }
        for p in pending_paths
    ]
    if not payloads:
        return results

    from concurrent.futures import ThreadPoolExecutor

    # Threads schedule hard-isolated processes (killable) without nested ProcessPools.
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {
            ex.submit(_run_one_isolated, pl, overall_timeout_s): pl for pl in payloads
        }
        done = 0
        for fut in as_completed(futures):
            done += 1
            res = fut.result()
            results.append(res)
            with open(log_path, "a") as f:
                f.write(json.dumps(res) + "\n")
            if done % 10 == 0 or res["status"] in ("valid", "pending_timeout") or done <= 5:
                logger.info(
                    "[pass%d %d/%d] %s task=%s cand=%s off=%s/%s dyn=%s/%s timeouts=%s",
                    pass_number,
                    done,
                    len(payloads),
                    res["status"],
                    res["task_id"],
                    res["candidate_id"],
                    res.get("official_passed"),
                    res.get("official_attempted"),
                    res.get("dynamic_passed"),
                    res.get("dynamic_attempted"),
                    res.get("timeouts"),
                )
    return results


def promote_valid(results: Sequence[dict]) -> int:
    VALID.mkdir(parents=True, exist_ok=True)
    n = 0
    for res in results:
        if res.get("status") != "valid":
            continue
        src = CANDIDATES / res["relative_path"]
        dest = VALID / res["task_id"] / Path(res["relative_path"]).name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        meta_src = src.with_suffix(src.suffix + ".meta.json")
        if meta_src.is_file():
            shutil.copy2(meta_src, dest.with_suffix(dest.suffix + ".meta.json"))
        (dest.with_suffix(dest.suffix + ".valid.json")).write_text(
            json.dumps(
                {
                    "candidate_id": res["candidate_id"],
                    "task_id": res["task_id"],
                    "source": res["source"],
                    "original_path": res["original_path"],
                    "license": res["license"],
                    "official_passed": res["official_passed"],
                    "dynamic_passed": res["dynamic_passed"],
                    "dynamic_generator_failures": res.get("dynamic_generator_failures", 0),
                    "n_dynamic_required": N_DYNAMIC,
                    "pass_number": res.get("pass_number", 1),
                },
                indent=2,
            )
        )
        n += 1
    return n


def coverage_report(results: Sequence[dict], v2_ids: Sequence[str]) -> dict:
    by_task: Dict[str, List[str]] = {tid: [] for tid in v2_ids}
    pending = []
    invalid = 0
    valid = 0
    for r in results:
        if r["status"] == "valid":
            valid += 1
            by_task.setdefault(r["task_id"], []).append(r["candidate_id"])
        elif r["status"] == "pending_timeout":
            pending.append(r["candidate_id"])
        else:
            invalid += 1
    covered = sum(1 for tid, cs in by_task.items() if cs)
    report = {
        "n_v2_tasks": len(v2_ids),
        "tasks_with_ge1_valid": covered,
        "tasks_with_zero_valid": len(v2_ids) - covered,
        "n_valid_candidates": valid,
        "n_invalid_candidates": invalid,
        "n_pending_timeout": len(pending),
        "pending_timeout_ids": pending,
        "per_task_valid_counts": {t: len(cs) for t, cs in sorted(by_task.items()) if cs},
        "uncovered_task_ids": sorted(t for t, cs in by_task.items() if not cs),
    }
    (LOGS / "coverage_report.json").write_text(json.dumps(report, indent=2))
    return report
