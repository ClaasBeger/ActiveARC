"""Slippage experiment helpers (narrow vs RE-ARC-broad verifier pairs)."""

from framework.slippage.pair_search import (
    SlippagePair,
    candidate_task_ids,
    find_slippage_pairs,
    find_slippage_pairs_for_task,
    save_slippage_pairs,
)

__all__ = [
    "SlippagePair",
    "candidate_task_ids",
    "find_slippage_pairs",
    "find_slippage_pairs_for_task",
    "save_slippage_pairs",
]
