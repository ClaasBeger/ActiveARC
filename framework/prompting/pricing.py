"""USD estimates for providers that do not report a billed cost.

OpenRouter returns ``usage.cost``; the OpenAI Responses API does not, so every
Luna summary in this repo has read ``total_cost: 0``. These are list prices per
million tokens, looked up 2026-09-20; cached input is billed at the cached rate.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

# model -> (input, cached_input, output), USD per 1M tokens
PRICES: Dict[str, tuple] = {
    "gpt-5.6-luna": (0.20, 0.02, 1.20),
}


def estimate_usd(model: Optional[str], usage: Optional[Dict[str, Any]]) -> Optional[float]:
    """Cost of one usage record, or None when the model has no price here."""
    if not model or not isinstance(usage, dict):
        return None
    key = next((m for m in PRICES if m in model), None)
    if key is None:
        return None
    p_in, p_cached, p_out = PRICES[key]
    total_in = usage.get("input_tokens") or 0
    cached = min(usage.get("cached_input_tokens") or 0, total_in)
    out = usage.get("output_tokens") or 0
    return ((total_in - cached) * p_in + cached * p_cached + out * p_out) / 1e6
