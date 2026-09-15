"""Score a finished trial's evidence on held-out items, in fresh context.

After exploration the model holds some pairs: the hot start plus whatever its
queries returned. This re-poses the task from those pairs alone, once per test
item, each in its own context. Two things follow from that.

The model no longer has its own reasoning transcript, so what is measured is
whether the *evidence it gathered* carries the rule -- the reset-copy reading,
separate from whether that particular conversation reached the right answer.

And because every item is asked independently, answering several of them cannot
leak between them, so the official items and the sampled one can both be scored
in the same trial without ordering effects.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from framework.active_arc.headless_trial import ActiveArcTrialSession
from framework.grids import Grid, is_equal_grid
from framework.prompting.clients import PROVIDER_OPENAI
from framework.prompting.evidence_prediction import predict_from_evidence


def _score_items(
    client: Any,
    session: ActiveArcTrialSession,
    items: List[tuple],
    *,
    model: str,
    reasoning_effort: Optional[str],
    max_turns: int,
    store: bool,
    provider: str,
) -> Dict[str, Any]:
    pairs = session.evidence_pairs_json()
    results: List[Dict[str, Any]] = []
    transcripts: List[Dict[str, Any]] = []
    for i, (test_in, gold) in enumerate(items):
        run = predict_from_evidence(
            client,
            pairs,
            test_in,
            model=model,
            reasoning_effort=reasoning_effort,
            max_turns=max_turns,
            store=store,
            provider=provider,
            test_index=i,
            n_tests=len(items),
        )
        pred = run["prediction"]
        results.append(
            {
                "index": i,
                "input": test_in,
                "gold_output": gold,
                "prediction": pred,
                "correct": pred is not None and is_equal_grid(pred, gold),
                "reason": run["reason"],
            }
        )
        transcripts.append({"index": i, "transcript": run["transcript"], "usage": run["usage"]})
    return {
        "items": results,
        "n_correct": sum(1 for r in results if r["correct"]),
        # All-or-nothing, to match how the static arm scores a multi-item task.
        "correct": bool(results) and all(r["correct"] for r in results),
        "transcripts": transcripts,
    }


def run_evidence_tests(
    client: Any,
    session: ActiveArcTrialSession,
    *,
    model: str,
    reasoning_effort: Optional[str],
    which: str = "both",
    max_turns: int = 8,
    store: bool = True,
    provider: str = PROVIDER_OPENAI,
) -> Dict[str, Any]:
    """Score the gathered evidence on the official items, the sampled one, or both.

    *which* is "official", "sampled" or "both". The sampled item is the one the
    trial itself drew, so scoring it here reproduces what the in-context answer
    was asked -- the difference between the two being the reasoning transcript.
    """
    out: Dict[str, Any] = {"n_evidence_pairs": len(session.evidence_pairs_json())}

    if which in ("official", "both"):
        items = session.official_test_items()
        if items:
            out["official"] = _score_items(
                client, session, items, model=model, reasoning_effort=reasoning_effort,
                max_turns=max_turns, store=store, provider=provider,
            )
        else:
            out["official"] = {"items": [], "n_correct": 0, "correct": None,
                               "transcripts": [], "unavailable": True}

    if which in ("sampled", "both"):
        pair = session.test_pair
        if pair is not None:
            out["sampled"] = _score_items(
                client, session, [(pair.input, pair.output)], model=model,
                reasoning_effort=reasoning_effort, max_turns=max_turns,
                store=store, provider=provider,
            )
        else:
            out["sampled"] = {"items": [], "n_correct": 0, "correct": None,
                              "transcripts": [], "unavailable": True}

    return out
